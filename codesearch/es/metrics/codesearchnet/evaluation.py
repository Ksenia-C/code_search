import logging
from typing import Callable, Dict, List, Union

import elasticsearch
from hyperopt import fmin, space_eval, tpe
from hyperopt import hp
import numpy as np
from tqdm import tqdm

from codesearch.es.client import ElasticSearchClient
from codesearch.es.metrics.codesearchnet.utils import timer
from codesearch.es.vs.v1 import transform_output_light

logger = logging.getLogger(__name__)


def top_n(dataset: List[Dict[str, str]],
          search_query_func: Callable[[str], Dict],
          client: ElasticSearchClient,
          index_name: str,
          n: int = 5,
          query_max_length: int = 30):
    logger.info("evaluation started!")
    score = 0.0
    cnt = len(dataset)

    for item in tqdm(dataset):
        query = item["query"][:query_max_length]  # feature
        location = item["location"]  # target

        try:
            result = client.instance.search(index=index_name, body=search_query_func(query))
        except elasticsearch.exceptions.TransportError as e:
            logger.error(e)
            cnt -= 1
            continue

        result = transform_output_light(result, keep_keys=["location"])

        for i, entity in enumerate(result):
            if i == n:
                break
            if entity["location"] == location:
                score += 1
                break

    return score / cnt


def make_search_query_func(identifiers_weight: int = 1,
                           split_identifiers_weight: int = 1,
                           function_body_weight: int = 1,
                           docstring_weight: int = 1,
                           location_weight: int = 1,
                           function_name_weight: int = 1,
                           prefix_length: int = 2,
                           match_type: str = "best_fields",
                           start: int = 0,
                           size: int = 5
                           ) -> Callable[[str], Dict]:
    return lambda query: {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            # exact occurrence
                            f"identifiers^{identifiers_weight}",
                            f"split_identifiers^{split_identifiers_weight}",
                            f"function_body^{function_body_weight}",
                            # meaning
                            f"docstring^{docstring_weight}",
                            f"location^{location_weight}",
                            f"function_name^{function_name_weight}"
                        ],
                        "type": match_type,
                        "fuzziness": "AUTO",
                        "prefix_length": prefix_length
                    }
                }
            }
        },
        "from": start,
        "size": size
    }


@timer
def find_best_params(dataset: List[Dict[str, str]],
                     client: ElasticSearchClient,
                     index_name: str,
                     grid: Dict[str, Union[Dict, List]],
                     n: int = 5,
                     query_max_length: int = 30,
                     max_evals: int = 50):
    best_score = 0.0

    def objective(args) -> float:
        nonlocal best_score
        args["size"] = n
        search_query_func = make_search_query_func(**args)

        # we want to maximize top_n, or minimize -top_n
        score = top_n(dataset, search_query_func, client, index_name, n, query_max_length)
        best_score = max(best_score, score)
        return -score

    # we should force docstring weight to be zero!!!
    space = {}
    # max_evals = 1
    for key in grid:
        value = grid[key]
        if isinstance(value, Dict):
            space[key] = hp.choice(key, np.arange(value["from"], value["to"], value["step"], dtype=int))
            # max_evals *= (abs(value["from"] - value["to"]) // value["step"])
        elif isinstance(value, List):
            space[key] = hp.choice(key, value)
            # max_evals *= len(value)
        else:
            raise ValueError(f"Unknown grid parameter: {key}:{value}")

    best = fmin(objective, space, algo=tpe.suggest, max_evals=max_evals)

    return best_score, space_eval(space, best)

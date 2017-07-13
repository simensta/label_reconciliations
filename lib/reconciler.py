"""Take the unreconciled data-frame and build the reconciled and explanations
data-frames.
"""

from functools import partial
import pandas as pd
import lib.util as util


def build(args, unreconciled, column_types):
    """This function builds the reconciled and explanations data-frames."""

    plugins = util.get_plugins('reconcilers')
    reconcilers = {k: plugins[v['type']] for k, v in column_types.items()}

    # Get group and then reconcile the data
    aggregators = {r: partial(reconcilers[r].reconcile, args=args)
                   for r in reconcilers
                   if r in unreconciled.columns}
    reconciled = unreconciled.groupby(args.group_by).aggregate(aggregators)

    # Split the combined value and explanation tuples into their own dataframes
    explanations = pd.DataFrame()
    for column in reconciled.columns:
        reconciler = reconcilers.get(column)
        if reconciler and reconciler.HAS_EXPLANATIONS:
            explanations[column] = reconciled[column].apply(lambda x: x[0])
            reconciled[column] = reconciled[column].apply(lambda x: x[1])

    return reconciled, explanations

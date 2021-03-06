"""Get mean median and mode for the group. Handle non-numeric characters."""

import re
import statistics as stats
import inflect


P = inflect.engine().plural


def reconcile(group, args=None):  # pylint: disable=unused-argument
    """Reconcile the data."""
    values = [g for g in group]

    numbers = []
    for value in values:
        try:
            numbers.append(float(value))
        except ValueError:
            pass

    if not numbers:
        reason = 'There are no numbers in {} {}'.format(
            len(values), P('record', len(values)))
        return reason, ''

    mean = stats.mean(numbers)
    mode = stats.mode(numbers)
    mode_count = len(n for n in numbers if n == mode)

    value = ('mean={:.2f}, mode={:.2f} (occurs {} {}) '
             'range=[{:.2f}, {:.2f}]').format(
                 mean,
                 mode,
                 mode_count,
                 P('time', mode_count),
                 min(numbers),
                 max(numbers))

    reason = 'There {} {} {} in {} {}'.format(
        P('is', len(numbers)),
        len(numbers), P('number', len(numbers)),
        len(values), P('record', len(values)))

    return reason, value


def adjust_reconciled_columns(reconciled, column_types):
    """Split reconciled results into separate Mean, Mode, & Range columns."""
    columns = {c for c in reconciled.columns
               if column_types.get(c, {'type': ''})['type'] == 'mmr'}
    for column in columns:
        reconciled[f'{column} Mean'] = reconciled[column].apply(
            lambda x: _get_mmr_part(x, r'mean=([0-9.]+)'))
        reconciled[f'{column} Mode'] = reconciled[column].apply(
            lambda x: _get_mmr_part(x, r'mode=([0-9.]+)'))
        reconciled[f'{column} Range lower'] = reconciled[column].apply(
            lambda x: _get_mmr_part(x, r'range=\[([0-9.]+)'))
        reconciled[f'{column} Range upper'] = reconciled[column].apply(
            lambda x: _get_mmr_part(x, r'range=\[[^,\s]+[,\s]*([0-9.]+)'))
    return reconciled.drop(columns, axis='columns')


def _get_mmr_part(value, regex):
    if not value:
        return ''
    match = re.search(regex, value)
    return match[1]

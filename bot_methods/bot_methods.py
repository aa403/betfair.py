__author__ = 'ammarorama'


def implied_percentage(**kwargs):
    r = {}
    for k, v in kwargs.items():
        if isinstance(v, (float)) and v > 0:
            r.update({k:round(1/v,5)})

        elif isinstance(v, (int, long)) and v > 0:
            r.update({k:round(1/float(v),5)})

        else:
            r.update({k:0.})

    return r

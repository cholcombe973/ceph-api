import six

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def validator(value, valid_type, valid_range=None):
    """
    Used to validate these: http://docs.ceph.com/docs/master/rados/operations/pools/#set-pool-values
    Example input:
        validator(value=1,
                  valid_type=int,
                  valid_range=[0, 2])
    This says I'm testing value=1.  It must be an int inclusive in [0,2]

    :param value: The value to validate
    :param valid_type: The type that value should be.
    :param valid_range: A range of values that value can assume.
    :return:
    """
    assert isinstance(value, valid_type), "{} is not a {}".format(
        value,
        valid_type)
    if valid_range is not None:
        assert isinstance(valid_range, list), \
            "valid_range must be a list, was given {}".format(valid_range)
        # If we're dealing with strings
        if valid_type is six.string_types:
            assert value in valid_range, \
                "{} is not in the list {}".format(value, valid_range)
        # Integer, float should have a min and max
        else:
            if len(valid_range) != 2:
                raise ValueError(
                    "Invalid valid_range list of {} for {}.  "
                    "List must be [min,max]".format(valid_range, value))
            assert value >= valid_range[0], \
                "{} is less than minimum allowed value of {}".format(
                    value, valid_range[0])
            assert value <= valid_range[1], \
                "{} is greater than maximum allowed value of {}".format(
                    value, valid_range[1])

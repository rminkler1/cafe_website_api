from hashlib import md5


def gravatar_url(
        email,
        size=32,
        rating='g',
        default='robohash',
        force_default="n"):
    """
    Convert email to gravatar url for gravatar image
    :param email: user email
    :param size: size in px
    :param rating:
    :param default: default image robots
    :param force_default: don't force default image
    :return: url
    """
    hash_value = md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"

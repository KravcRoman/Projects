class Null:
  """ Null objects always and reliably "do nothing." """

  def __init__(self, *args, **kwargs):
    pass

  def __call__(self, *args, **kwargs):
    return self

  def __repr__(self):
    return "Null(  )"

  def __nonzero__(self):
    return 0
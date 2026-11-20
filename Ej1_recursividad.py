def producto(a, b):
  if b == 1:
    return a
  return a + producto(a, b - 1)
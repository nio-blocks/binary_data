PackBytes
=========
Convert numeric values to binary data.

Properties
----------
- **new_attributes**: Outgoing signal attributes to store each converted piece of binary data.
  - *format*: Data type to convert, select one of `[integer, unsigned_integer, float]`.
  - *endian*: Select `big` or `little` byte order.
  - *length*: How many bytes to store the value, select one of `[2, 4, 8]`.
  - *key*: Outgoing signal attribute to store the packed binary data.
  - *value*: Numeric value to pack.

Inputs
------
- **default**: Any list of signals

Outputs
-------
- **default**: A list of signals of equal length to input signals, where each signal contains the converted `key: value` pairs in `new_attributes`.

Commands
--------
None

***

UnpackBytes
===========
Convert binary data into numeric values.

Properties
----------
- **new_attributes**: Outgoing signal attributes to store each converted piece of binary data.
  - *format*: Data type to convert, select one of `[integer, unsigned_integer, float]`.
  - *endian*: Select `big` or `little` byte order.
  - *key*: Outgoing signal attribute to store the numeric value.
  - *value*: Binary data to unpack.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: A list of signals of equal length to input signals, where each signal contains the converted `key: value` pairs in `new_attributes`.

Commands
--------
None


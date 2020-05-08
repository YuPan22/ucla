# binfilepy

Software library to read and write binary file (.adibin format).

## Example to write a binary file:
```
from binfilepy import BinFile
from binfilepy import CFWBINARY
from binfilepy import CFWBCHANNEL

with BinFile(filename, "w") as f:
    header = CFWBINARY()
    header.setValue(1.0 / 240.0, 2019, 1, 28, 8, 30, 0.0, 0.0, 2, 0)
    f.setHeader(header)
    channel1 = CFWBCHANNEL()
    channel1.setValue("I", "mmHg", 1.0, 0.0)
    f.addChannel(channel1)
    channel2 = CFWBCHANNEL("II", "mmHg", 1.0, 0.0)
    f.addChannel(channel2)
    chanData = []
    d1 = [1, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 1]
    d2 = [8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8]
    chanData.append(data1)
    chanData.append(data2)
    f.writeHeader()
    f.writeChannelData(chanData)
    f.updateSamplesPerChannel(16, True)
```

## Example to read a binary file:
```
from binfilepy import BinFile

with BinFile(filename, "r") as f:
    # You must read header first before you can read channel data
    f.readHeader()
    # readChannelData() supports reading in random location (Ex: Read 10 secs of data at 1 min mark)
    data = f.readChannelData(offset=60, length=10, useSecForOffset=True, useSecForLength=True)
```

## File open mode
Currently, there are three modes to open a file:
- "w": For writing to a new file.  You need to make sure the file doesn't exist.
- "r": For reading from an existing file.  You need to make sure the file exists.
- "r+": For appending data to an existing file.  You need to make sure the file exists.

You can use either syntax:
```
with BinFile(filename, "w") as f:
    ...
    ...
```
or
```
f = BinFile(filename, "w")
f.open()
...
...
f.close()
```

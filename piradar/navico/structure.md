
# Send 
__Little endiness__

_Address: (236.6.7.10:6680) or (236.6.7.14 6658)_

Commands:
+ C1: Write to a registry.
+ C2: Read from a registry.

|         | Registry | Command | Payload |
|:--------|---------:|--------:|--------:|
| *byte length* |        1 |       1 |       N |
| Write   |   varies |      C1 |  varies |
| Read    |   varies |      C2 |  varies |


## Write

Commands are sent to the radar by writing values with the C1 command to a given registry.

### Transmit On & Off

Start and stop radar.
Both TxOnA and TxOnB need to be sent to start the radar
and likewise to stop it (TxOffA, TxOffB).

|               | Registry | Command | Value |
|:--------------|---------:|--------:|------:|
| *byte length* |        1 |       1 |     1 |
| TxOnA         |       00 |      C1 |    01 |
| TxOnB         |       01 |      C1 |    01 |
| TxOffA        |       00 |      C1 |    01 |
| TxOffB        |       01 |      C1 |    00 |

### Range | Registry 03

Value are unsigned integer

|               | Registry | Command | Range Value |
|:--------------|---------:|--------:|------------:|
| *byte length* |        1 |       1 |           4 |
|               |       03 |      C1 | XX XX XX XX |


### Bearing | Registry 05
Value is and unsigned integer

|               | Registry | Command | Bearing      Value |
|:--------------|---------:|--------:|-------------------:|
| *byte length* |        1 |       1 |                  2 |
|               |       05 |      C1 |              XX XX |


### Registry 06 (auto on/off and values)

Auto and Value are unsigned integers

|                        |  Registry |  Command |  Sub Command |      Fill |  Auto |      Fill |  Value |
|:-----------------------|----------:|---------:|-------------:|----------:|------:|----------:|-------:|
| *byte length*          |         1 |        1 |            1 |         3 |     1 |         3 |      1 |
| Gain                   |        06 |       01 |           00 |  00 00 00 |    XX |  00 00 00 |     XX |
| Sea Clutter            |        06 |       01 |           02 |  00 00 00 |    XX |  00 00 00 |     XX |
| Rain Clutter           |        06 |       01 |           04 |  00 00 00 |    XX |  00 00 00 |     XX |
| Side Lobe Suppression  |        06 |       01 |           05 |  00 00 00 |    XX |  00 00 00 |     XX |


### 1 Byte commands:
For automatic settings.

|                           | Registry | Command | Value |
|:--------------------------|---------:|--------:|------:|
|                           |        1 |       1 |     1 |
| Interference Rejections   |       08 |      C1 |    XX |
| Target Boost              |       0a |      C1 |    XX |
| Sea State                 |       0b |      C1 |    XX |
| Local Interference Filter |       0e |      C1 |    XX |
| Scan Speed                |       0f |      C1 |    XX |
| Mode                      |       10 |      C1 |    XX |
| Target Expansion          |       12 |      C1 |    XX |
| Noise Rejection           |       21 |      C1 |    XX |
| Target Separation         |       22 |      C1 |    XX |
| Doppler Mode              |       23 |      C1 |    XX |

Value mapping

|                                    |     00 |       01 |               02 | 03      | 05   |
|:-----------------------------------|-------:|---------:|-----------------:|---------|------|
| Interference Rejections            |    off |      low |           medium | high    | -    |
| Target Boost                       |    off |      low |             high | -       | -    |
| Sea State                          |   calm | moderate |            rough | -       | -    |
| Local Interference Filter          |    off |      low |           medium | high    | -    |
| Scan Speed  (unsure, BR24 ?)       | normal |     fast |                - | -       | -    |
| Scan Speed  (unsure, G and Halo ?) |   slow |   normal |             fast | -       | -    |
| Mode                               | custom |   harbor |         offshore | weather | bird |
| Target Expansion                   |    off |      low |           medium | high    | -    |
| Noise Rejection                    |    off |      low |           medium | high    | -    |
| Target Separation                  |    off |      low |           medium | high    | -    |
| Doppler Mode                       |    off |   normal | approaching_only | -       | -    |

### Auto Sea Clutter Nudge (unsure)


### Doppler Speed 24


### Antenna Height 30


### Light 31
# Xreg
A Python plugin for GDB to help debugging Cortex-M MCU

This project is inspired by [cmsis-svd](https://github.com/posborne/cmsis-svd) and [gdb-regview](https://github.com/fnoble/gdb-regview) these two amazing projects.



Where this name comes from? x is memory show command in GDB, reg is short for register!



## 1. Features

* Single file, no dependencies
* Support standard cmsis svd file



## 2. How to use

Currently, you need to first import the script in GDB

```
source /path/to/Xreg.py
```

Then load the svd file

```
xreg load /path/to/svd/file
```

And have fun!



## 3. Commands

### 1. show

Show all the registers value of a peripheral

```
xreg show [peripheral]
```

Show certain register value of a peripheral

```
xreg show [peripheral]_[register]
```



### 2. list

List all the peripherals

```
xreg list
```

List all the registers of a peripheral

```
xreg list [peripheral]
```


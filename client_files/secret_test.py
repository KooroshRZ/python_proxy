import binascii, angr, simuvex, archinfo, pyvex
filename = '/home/ehsan/Desktop/ls'
with open(filename, 'rb') as f:
    content = f.read()
irsb = pyvex.IRSB(binascii.hexlify(content), archinfo.ArchARM())
irsb.pp()
irsb.next.pp()
 
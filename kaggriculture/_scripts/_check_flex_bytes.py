data = open(r'D:\桌面\Kaggle\kaggriculture\_external\top5_notebooks\flexonafft\flexonafft_main.py','rb').read()
print('len', len(data))
print('0x0A count', data.count(b'\x0a'))
print('0x0D count', data.count(b'\x0d'))
print('0x5C count', data.count(b'\\'))
for i, b in enumerate(data):
    if b in (0x0A, 0x0D):
        print('first line ending at', i, hex(b))
        print('context:', repr(data[max(0,i-20):i+20]))
        break

#%%
def createBashFile(imageName):
	with open('build.sh', 'w') as b:
		b.write('docker build -t {} .\n'.format(imageName.lower()))
		b.write('docker save -o ./images/{} {}\n'.format(imageName.lower(), imageName.lower()))


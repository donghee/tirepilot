from distutils.core import setup
import py2exe
import glob

options = {
	"bundle_files": 1,
	"compressed" : 1,
}

setup(
	windows=[{'script':'app.py', 'icon_resources':[(1,'tirepilot.ico')]}],
	zipfile = None,
	data_files = [("images", glob.glob("images/*")), ("resources", glob.glob("resources/*"))]
)

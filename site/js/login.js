import { pageScript } from './modules/login'
import facebook from './modules/script'
import FaceBook from './modules/fb'
	
window.facebook = new FaceBook(pageScript)
$(document).ready(pageScript.main)
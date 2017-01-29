import { pageScript } from './modules/login'
import facebook from './modules/script'
import FaceBook from './modules/fb'
import x from './modules/back_to_top' //back to top button
	
window.facebook = new FaceBook(pageScript)
$(document).ready(pageScript.main)
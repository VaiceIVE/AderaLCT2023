const express = require('express')
const StorageController = require('../Controllers/StorageController')
const uploader = require('../Services/UploadHelperService')
const router = express()


router.post('/upload', uploader.single('file'), StorageController.UploadFile)
router.get('/file/:filename', StorageController.GetFile)
router.post('/url', StorageController.DownloadByUrl)
router.get('/list', StorageController.List)





module.exports = router

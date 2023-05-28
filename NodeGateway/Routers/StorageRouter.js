const express = require('express')
const uploader = require('../Services/UploadHelperService')
const StorageController = require('../Controllers/StorageController')
const router = express()

router.get('/list', StorageController.GetList)
router.get('/file/:filename', StorageController.GetFile)
//list and fileget

module.exports = router

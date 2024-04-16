
var API_HOST = process.env.API_HOST;
var API_PORT = process.env.API_PORT;
if (API_HOST === undefined){
    API_HOST = "90.156.208.248"
}
if (API_PORT === undefined){s
    API_PORT = "8000"
}
const Configs = {
    API_URL: `http://${API_HOST}:${API_PORT}/api`,
    NUM_FILES: 3,
    ERROR_CODE: {
        USER_NOT_FOUND:"USER_NOT_FOUND",
        EXISTED_USER:"EXISTED_USER",
        VOICE_NOT_FOUND:"VOICE_NOT_FOUND",
        ERROR_INTERNAL:"ERROR_INTERNAL"
    }
}
export default Configs;
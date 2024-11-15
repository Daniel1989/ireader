import Device from '@skillnull/device-js'

let initDeviceId = ''
// export const HOST = "http://127.0.0.1:7860"
export const HOST = process.env.NODE_ENV === 'production' ? '' : 'http://127.0.0.1:8000'

export const CLIENT_ID = async () => {
    if(initDeviceId) {
        return initDeviceId
    }
    const data = await Device.Info()
    initDeviceId = data.fingerprint
    return initDeviceId
}


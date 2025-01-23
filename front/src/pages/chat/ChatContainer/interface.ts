export interface IMessage {
    user: string,
    text: string,
    avatar: string,
    pending: boolean,
    error?: string,
    sources?: {
        url: string, 
        title: string, 
        similarity: string,
    }[]
}
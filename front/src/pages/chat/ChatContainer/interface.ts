export interface IMessage {
    user: string,
    text: string,
    avatar: string,
    pending: boolean,
    error?: string,
}
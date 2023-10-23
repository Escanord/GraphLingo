export interface IChatResponse<T = any> {
    msg: string;
    data?: T;
}
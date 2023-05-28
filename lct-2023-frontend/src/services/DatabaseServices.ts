import { AxiosResponse } from "axios";
import $api from "../http";

export default class DatabaseServices {
    
    static fetchDatabase(): Promise<AxiosResponse<string[]>> {
        return $api.get<string[]>('/storage/list');
    };

    static async databaseExport(name: string): Promise<AxiosResponse<Blob>> {
        return $api.get<Blob>(`/storage/file/${name}`, {responseType: 'blob'});
    };
};

import { useContext, useEffect } from "react";
import { Context } from "../../../main";
import { observer } from "mobx-react-lite";
import DatabaseServices from "../../../services/DatabaseServices";
import DatabaseItem from "./DatabaseItem";
import BlockWrapper from "../../../components/Wrappers/BlockWrapper";
import { Stack } from "@mantine/core";

const DatabaseList = () => {
    const { DStore } = useContext(Context);

    useEffect(() => {
        let isCancelled = false;
        try {
            DatabaseServices.fetchDatabase().then((response) => {
                if (!isCancelled) { 
                    DStore.setDatabase(response.data);
                }
            });
        } catch (e) {
            console.log(e);
        };

        return () => {
            isCancelled = true;
        }
    }, []);

    return (
        <BlockWrapper>
            Файлы в хранилище
            <Stack spacing={8}>
                {DStore.database && 
                    DStore.database.map(item => (
                        <DatabaseItem key={item} file={item}/>
                    ))
                }
            </Stack>
            
        </BlockWrapper>
    );
};

export default observer(DatabaseList);
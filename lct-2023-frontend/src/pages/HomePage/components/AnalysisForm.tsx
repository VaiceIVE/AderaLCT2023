import { Button, Flex, Stack } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Context } from "../../../main";
import { CURRENT_ANALYSIS_ROUT } from "../../../utils/const";
import AnalysisInput from "./AnalysisInput";
import AnalysisOrigin from "./AnalysisOrigin";



const AnalysisForm = () => {
    const { AStore } = useContext(Context);
    const navigate = useNavigate();

    const [date, setDate] = useState<[Date | null, Date | null]>([null, null]);
    const [object, setObject] = useState<string>('');
    const [work, setWork] = useState<string>('');
    const [origin, setOrigin] = useState<string>('database');
    const [url, setUrl] = useState<string>('');
    const [btnDisabled, setBtnDisabled] = useState<boolean>(true);

    useEffect(() => {
        if (origin === 'database') {
            if ((date[0]!=null && date[1]!=null) && object && work) {
                setBtnDisabled(false);
            } else {
                setBtnDisabled(true);
            }
        } else if (origin === 'url') {
            if ((date[0]!=null && date[1]!=null) && object && work && url) {
                setBtnDisabled(false);
            } else {
                setBtnDisabled(true);
            }
        } 
    }, origin==='url' ? [work, date, object, url] : 
    [work, date, object, origin])

    const handlePost = async () => {
        if (origin === 'database') {
            console.log(date)
            AStore.smartAnalysisDatabase(object, date, work);
        }; 
    };

    return (
        <Flex gap={24} align="flex-end">
            <Stack spacing={24}>
            <AnalysisInput 
                work={work}
                setWork={setWork}
                object={object}
                setObject={setObject}
                date={date}
                setDate={setDate}
            />
            <AnalysisOrigin url={url} setUrl={setUrl} setOrigin={setOrigin} origin={origin}/>
            </Stack>
            <Button
                fz='lg'
                w={164} h={48}
                color={AStore.currentSmartAnalysis ? 'red.7' : 'gray.9'}
                fw={400}
                disabled={btnDisabled}
                onClick={AStore.currentSmartAnalysis ? 
                    () => navigate(CURRENT_ANALYSIS_ROUT + '/' + 0) :
                    () => handlePost() 
                }
            >
                {AStore.currentSmartAnalysis ? 'К результату' : 'Начать'}
            </Button>
        </Flex>
    );
};

export default observer(AnalysisForm);
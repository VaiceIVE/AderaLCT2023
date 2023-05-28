import { Modal, Stack } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { observer } from "mobx-react-lite";
import { FC, useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Wrapper from "../../components/Wrappers/Wrapper";
import { Context } from "../../main";
import { IAnalysis } from "../../models/IAnalysis";
import { IAnalysisResult } from "../../models/IAnalysisResult";
import AnalysisServices from "../../services/AnalysisServices";
import AnalysisResult from "./components/AnalysisResult";
import FileExport from "./components/FileExport";
import InfoBlock from "./components/InfoBlock";
import ModalEdit from "./components/ModalEdit";
import ModalInfo from "./components/ModalInfo";


const CurrentAnalysisPage: FC = () => {
    const { AStore } = useContext(Context);
    const [analysisResult, setAnalysisResult] = useState<IAnalysis>();
    const [result, setResult] = useState<IAnalysisResult[]>();
    const [works, setWorks] = useState<string[]>();
    const [adressEdit, setAdressEdit] = useState<string | undefined>();
    const [adressInfo, setAdressInfo] = useState<string | undefined>();
    const [openedInfo, setOpenInfo] = useState<boolean>(false);
    const [opened, { open, close }] = useDisclosure(false);
    const {id} = useParams();
    
    useEffect(() => {
        let isCancelled = false;
        if (id === '0') {
            setAnalysisResult(AStore.currentBaseAnalysis || AStore.currentSmartAnalysis);
            setResult(AStore.currentBaseAnalysis?.result || AStore.currentSmartAnalysis?.result);
        } else {
            try {
                AStore.setBaseLoading(true);
                AnalysisServices.selectAnalysis(id ? id : '1').then((response) => {
                    if (!isCancelled) {
                        console.log(response.data) 
                        setAnalysisResult(response.data);
                        setResult(response.data.result);
                    };
                });
            } catch (e) {
                console.log(e);
            } finally {
                AStore.setBaseLoading(false);
            };
        }
        return () => {
            isCancelled = true;
        }
    }, []);

    useEffect(() => {
        setAnalysisResult((item) => ({...item!, result}));
    }, [result]);

    useEffect(() => {
        AStore.setAnalysis(analysisResult);
    }, [analysisResult || result]);

    useEffect(() => {
        result?.map((item: any) => {
            if (item.adress === adressEdit) {
                const changeableАddress = item;
                changeableАddress.workname = works;
                const indexToReplace = result!.findIndex((res) => res.adress === adressEdit);
                const newState = result?.map((item: any, index: number) => {
                    if (index === indexToReplace) {
                        return {...item, workname: works};
                    };
                    return item;
                })
                setResult(newState);
            }
        })
    }, [works]);

    const handleAdressDelete = (adress:string) => {
        setResult((item) => {
            return item?.filter(result => result.adress != adress) 
        });
    };

    const handleSetWorks = (works: string[], _adress: string) => {
        if (_adress) {
            setWorks(works);
            setAdressEdit(_adress);
        } else {
            setWorks(works);
        };
    };

    const handleModalInfoClose = () => {
        setOpenInfo(false);
    };

    const handleModalOpen = (adress: string) => {
        setAdressInfo(adress);
        setOpenInfo(true)
    };

    return (
        <div>
            {analysisResult &&
            <Wrapper>
                <Stack spacing={24}>
                    <InfoBlock criterias={analysisResult.criterias} type={analysisResult.type!}/>
                    <AnalysisResult 
                        open={open} 
                        handleAdressDelete={handleAdressDelete} 
                        {...analysisResult}
                        handleSetWorks={handleSetWorks}
                        handleModalOpen={handleModalOpen}
                    />
                    <Modal
                        opened={openedInfo} onClose={() => setOpenInfo(false)}
                        lockScroll={false}
                        trapFocus={false}
                        style={{zIndex: 10000000, position: 'absolute'}} 
                        centered
                        withCloseButton={false}
                        padding={'32px'}
                        size={600}
                    >
                        <ModalInfo
                            adress={adressInfo!}
                            {...analysisResult}
                            handleModalInfoClose={handleModalInfoClose}
                        />
                    </Modal>
                    <Modal
                        size={508}
                        lockScroll={false}
                        trapFocus={false}
                        style={{zIndex: 10000000, position: 'absolute'}} 
                        opened={opened} onClose={close} 
                        centered
                        withCloseButton={false}
                        padding={'32px'}
                    >
                        <ModalEdit 
                            handleSetWorks={handleSetWorks} 
                            onClose={close} works={works}
                        />
                    </Modal>
                </Stack>
                <FileExport id={analysisResult.id}/>
            </Wrapper>
            }
        </div>
    );
};

export default observer(CurrentAnalysisPage);

import BlockWrapper from "../../../components/Wrappers/BlockWrapper";
import { IAnalysisResult } from "../../../models/IAnalysisResult";
import Example from "./ResultTable";

const AnalysisResult = (props: {result: IAnalysisResult[] | undefined, 
    handleAdressDelete: Function, open: () => void, handleSetWorks: Function,
    handleModalOpen: Function
}) => {
    
    return (
        <BlockWrapper>
            Рекомендуемые работы
            {props.result && 
                <Example 
                    handleModalOpen={props.handleModalOpen}
                    open={props.open} 
                    handleAdressDelete={props.handleAdressDelete} 
                    result={props.result}
                    handleSetWorks={props.handleSetWorks}
                />
            }
        </BlockWrapper>
    );
};

export default AnalysisResult;
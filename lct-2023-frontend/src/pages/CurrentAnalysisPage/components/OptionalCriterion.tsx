import { Stack, Text } from "@mantine/core";
import AnalysisInput from "../../HomePage/components/AnalysisInput";

const OptionalCriterion = (props: {criterias: string[] | undefined}) => {

    return (
        <Stack spacing={16}>
            <Text color="gray.5" size="md" lh={'20px'}>Опциональные</Text>
            {props.criterias &&
                <AnalysisInput
                    object={props.criterias![0] ? props.criterias![0] : ''}  
                    work={props.criterias![1] ? props.criterias![1] : ''} 
                    date={
                        [new Date(props.criterias[2].toString().substring(0,10)),
                        new Date(props.criterias[2].toString().substring(25,35))]
                    } 
                    disabled={true}
                />
            }
        </Stack>
    );
}

export default OptionalCriterion;
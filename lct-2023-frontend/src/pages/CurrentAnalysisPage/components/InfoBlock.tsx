import { createStyles, Flex } from "@mantine/core";
import BlockWrapper from "../../../components/Wrappers/BlockWrapper";
import MainCriterion from "./MainCriterion";
import OptionalCriterion from "./OptionalCriterion";

const useStyles = createStyles((theme) => ({

    wrapper: {
        padding: '24px',
        background: theme.colors.gray[0],
        borderRadius: '16px',
    }
}))

const InfoBlock = (props: {type: string, criterias: string[] | undefined}) => {
    const { classes } = useStyles();

    return (
        <Flex className={classes.wrapper}>
            <BlockWrapper >
                Используемые критерии
                <MainCriterion/>
                {props.type === 'base' ? <></> :
                    <OptionalCriterion criterias={props.criterias}/>
                }
            </BlockWrapper>
        </Flex>
    );
};

export default InfoBlock;
import { Accordion, createStyles } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import Wrapper from "../../components/Wrappers/Wrapper";

const useStyles = createStyles(() => ({
    wrapper: {
        width: '800px',
    }
}));

const HelpPage = () => {
    const { classes } = useStyles();

    return (
        <Wrapper>
            <Accordion
                className={classes.wrapper}
                defaultValue="customization"
                chevron={<IconPlus stroke={'2'} />}
                styles={{
                    chevron: {
                    '&[data-rotate]': {
                        transform: 'rotate(45deg)',
                    },
                    },
                }}
                fz="lg"
                lh={'24px'}
            >
                <Accordion.Item value="customization">
                    <Accordion.Control style={{padding: '16px 24px'}} fz='lg' lh={'24px'}>
                        Что за режимы анализа?
                    </Accordion.Control>
                    <Accordion.Panel>
                        Режим “Базовый” основывается исключительно на анализе обязательных критериев для нашего алгоритма. 
                        В нем пользователю не придется вводить исходные данные.
                        Режим же “Продвинутый” позволяет вам выбрать один из трех вариантов указания дополнительных данных. 
                        Здесь наш алгоритм будет учитывать еще и данные, введенные пользователем.
                    </Accordion.Panel>
                </Accordion.Item>

                <Accordion.Item value="flexibility">
                    <Accordion.Control style={{padding: '16px 24px'}} fz='lg' lh={'24px'}>
                        Какие виды исходных данных есть?
                    </Accordion.Control>
                    <Accordion.Panel>
                    Загрузка: вы можете загрузить с компьютера файл с таблицами данных, 
                    на основе которых алгоритм будет делать предсказания.
                    База данных: на основе основной базы данных из датасета, 
                    вы можете указать дополнительные критерии для анализа.
                    Сторонние сервисы: подгрузка данных с сторонних API
                    </Accordion.Panel>
                </Accordion.Item>

                <Accordion.Item value="focus-ring">
                    <Accordion.Control style={{padding: '16px 24px'}} fz='lg' lh={'24px'}>
                        Обучение алгоритма после изменений
                    </Accordion.Control>
                    <Accordion.Panel>
                        Меняя поля результата анализа и сохраняя их по кнопке “Сохранить”, 
                        вы отправляете алгоритму дополнительные основания для следующих анализов. 
                        Если вы удалили что-то лишнее или сделали это случайно, сохранив поля, 
                        просто не нажимайте кнопку сохранения всего результата в правом верхнем углу экрана.
                    </Accordion.Panel>
                </Accordion.Item>

                <Accordion.Item value="focus-rin">
                    <Accordion.Control style={{padding: '16px 24px'}} fz='lg' lh={'24px'}>
                        Проверка правильности анализа пользователя
                    </Accordion.Control>
                    <Accordion.Panel>
                        На момент Хакатона мы добавили возможность авторизации в аккаунт старшего аналитика, 
                        где планируется подтверждение изменений других аналитиков. 
                        Это делается для того, чтобы модель не получала заведомо неверных данных.
                        Скорее всего, в планах дальнейшего обучения модели, 
                        в какой-то момент дополнительная проверка человеком не понадобится, 
                        так как модель сможет отсеивать “неверные” изменения.
                    </Accordion.Panel>
                </Accordion.Item>
            </Accordion>
            <></>
        </Wrapper>
    );
};

export default HelpPage;
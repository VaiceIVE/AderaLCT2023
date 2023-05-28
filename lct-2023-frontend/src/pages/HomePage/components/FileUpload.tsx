import { Text, useMantineTheme, Flex } from '@mantine/core';
import { IconUpload, IconFile, IconX } from '@tabler/icons-react';
import { Dropzone, MS_EXCEL_MIME_TYPE } from '@mantine/dropzone'

const FileUpload = () => {
  const theme = useMantineTheme();

  return (
    <Dropzone
      onDrop={(files) => console.log('accepted files', files)}
      onReject={(files) => console.log('rejected files', files)}
      w={759}
      h={166}
      accept={MS_EXCEL_MIME_TYPE}
      padding="0"
      bg="#F1F3F5"
    >
      <Flex align="center" justify="center" gap={16} h={166}>
        <Dropzone.Accept>
          <IconUpload
            size="3.2rem"
            stroke={1.5}
            color={theme.colors[theme.primaryColor][theme.colorScheme === 'dark' ? 4 : 6]}
          />
        </Dropzone.Accept>

        <Dropzone.Reject>
          <IconX
            size="3.2rem"
            stroke={1.5}
            color={theme.colors.red[theme.colorScheme === 'dark' ? 4 : 6]}
          />
        </Dropzone.Reject>

        <Dropzone.Idle>
          <IconFile size="3.2rem" stroke={1.5} />
        </Dropzone.Idle>

        <div>
          <Text lh={'28px'} size="xl" color="gray.9">
            Перетащите или нажмите, чтобы выбрать файл
          </Text>
          <Text lh={'24px'} size="lg" color="gray.6" mt={2}>
            Прикрепите файл в формату .xlsx, .xls
          </Text>
        </div>
      </Flex>
    </Dropzone>
    );
};

export default FileUpload;
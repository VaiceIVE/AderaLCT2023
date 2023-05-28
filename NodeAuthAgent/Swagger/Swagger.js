const swaggerAutogen = require('swagger-autogen')()

const outputFile = './swagger_output.json'
const endpointsFiles = ['./Routers/UserRouter.js']
const doc = {
    info: {
      title: 'Агент авторизации',
      description: 'Агент для авторизации пользователей в сервисе написанный на NodeJS с хранением данных пользователей на MongoDB',
    },
    definitions: {
        UserResponse:{
            $refreshToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey3JlbWFpbCI6InNva29sb3Zyb21hbjI1NkBnbWFpbC5jb20iLCJpZCI6IjY0Njc3YjY2MzdkNTljN2QyYTE4ZDU4MyIsInVzZXJuYW1lIjoi0KHQvtC60L7Qu9C-0LIg0KDQvtC80LDQvSIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjg0ODQ4MjkzLCJleHAiOjE2ODY5MjE4OTN9.nvOexFSAQnIFeqT9nv73QnHDWFhoqXKim7TJObvnm_o",
            $accessToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNva29sb3Zyb21hbjI1NkBnbWFpbC5jb20iLCJpZCI6IjY0Njc3YjY2MzdkNTljN2QyYTE4ZDU4MyIsInVzZXJuYW1lIjoi0KHQvtC60L7Qu9C-asddlkfvjsdjhfvblakwjhdvfblkjwvbfhkhssd4MjkzLCJleHAiOjE2ODY5MjE4OTN9.nv'lkgjgwljfghojejfhgsdfgkjsdhfhggalsgajfhg'_o",
            user:
            {
                $username: 'Соколов Роман',
                $id: "646b156e5f5735bddb9db7fd",
                $email: 'sokolovroman@mail.ru',
                $role: 'Старший аналитик' 
            }
        },
        UserReg:{
            $username: 'Соколов Роман',
            $email: 'sokolovroman@mail.ru',
            $password: 'Roma`s password',
            $role: 'Старший аналитик' 
        },
        UserLog:{
            $email: 'sokolovroman@mail.ru',
            $password: 'Roma`s password',
            $role: 'Старший аналитик' 
        },
        RefreshToken:{
            $refreshToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey3JlbWFpbCI6InNva29sb3Zyb21hbjI1NkBnbWFpbC5jb20iLCJpZCI6IjY0Njc3YjY2MzdkNTljN2QyYTE4ZDU4MyIsInVzZXJuYW1lIjoi0KHQvtC60L7Qu9C-0LIg0KDQvtC80LDQvSIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjg0ODQ4MjkzLCJleHAiOjE2ODY5MjE4OTN9.nvOexFSAQnIFeqT9nv73QnHDWFhoqXKim7TJObvnm_o"
        },
        AccessToken:{
            $accessToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNva29sb3Zyb21hbjI1NkBnbWFpbC5jb20iLCJpZCI6IjY0Njc3YjY2MzdkNTljN2QyYTE4ZDU4MyIsInVzZXJuYW1lIjoi0KHQvtC60L7Qu9C-asddlkfvjsdjhfvblakwjhdvfblkjwvbfhkhssd4MjkzLCJleHAiOjE2ODY5MjE4OTN9.nv'lkgjgwljfghojejfhgsdfgkjsdhfhggalsgajfhg'_o"
        },
        LogOut:{
            $acknowledged: true,
            $deletedCount: 1
        }
      },

    host: '87.242.91.93:8000',
    schemes: ['http'],
    
  };
swaggerAutogen(outputFile, endpointsFiles, doc)

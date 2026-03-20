import Mock from 'mockjs';

// 模拟登录接口 - 已切换至真实接口 /api/v1/auth/admin/login
// Mock.mock('/api/login', 'post', (options) => {
//   const { username, password } = JSON.parse(options.body);
//   if (username === 'admin' && password === '123456') {
//     return {
//       code: 200,
//       message: '登录成功',
//       data: {
//         token: 'mock-token-123456',
//         user: {
//           id: 1,
//           username: 'admin',
//           name: '管理员'
//         }
//       }
//     };
//   } else {
//     return {
//       code: 401,
//       message: '用户名或密码错误'
//     };
//   }
// });

// 模拟注册接口 - 已切换至真实接口 /api/v1/auth/admin/register
// Mock.mock('/api/register', 'post', (options) => {
//   return {
//     code: 200,
//     message: '注册成功'
//   };
// });

// 模拟获取用户信息 - 已切换至真实接口 /api/v1/users/me
// Mock.mock('/api/user/info', 'get', {
//   code: 200,
//   message: '获取成功',
//   data: {
//     id: 1,
//     username: 'admin',
//     name: '管理员',
//     roles: ['admin']
//   }
// });

export default Mock;

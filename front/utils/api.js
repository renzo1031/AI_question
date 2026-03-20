const api = {
  auth: {
    sendCode: '/auth/verify-code/send',
    registerPhone: '/auth/register/phone',
    registerEmail: '/auth/register/email',
    login: '/auth/login/password',
    loginCode: '/auth/login/verify-code',
    refreshToken: '/auth/token/refresh',
    resetPassword: '/auth/password/reset',
    logout: '/auth/logout'
  },
  user: {
    me: '/user/info',
    updateMe: '/user/info', // PUT
    password: '/user/password/change',
    bindPhone: '/user/bind/phone',
    bindEmail: '/user/bind/email'
  },
  upload: {
    sts: '/upload/sts'
  },
  ai: {
    search: '/question/solve/image/upload',
    solveText: '/question/solve/text'
  },
  announcement: {
    active: '/announcements/active'
  },
  banner: {
    active: '/banners/active'
  },
  correction: {
    submit: '/corrections',
    my: '/corrections/my'
  },
  wrongBook: {
    list: '/wrongbook',
    practice: '/wrongbook/practice/generate'
  },
  learning: {
    overview: '/learning/overview',
    ability: '/learning/ability',
    feedback: '/learning/feedback'
  },
  practice: {
    generate: '/practice/generate',
    answer: (id) => `/practice/questions/${id}/answer`
  }
};

module.exports = api;

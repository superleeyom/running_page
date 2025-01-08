interface ISiteMetadataResult {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
  }[];
}

const data: ISiteMetadataResult = {
  siteTitle: '我的跑步日志',
  siteUrl: 'https://running.leeyom.top',
  logo: 'https://raw.githubusercontent.com/superleeyom/running_page/master/public/images/myheader3.jpeg',
  description: '喜欢强风吹拂的感觉~',
  navLinks: [
    {
      name: 'Blog',
      url: 'https://blog.leeyom.top',
    },
    {
      name: 'About',
      url: 'https://github.com/superleeyom',
    },
  ],
};

export default data;

const menu = [
  {
    label: 'Blog',
    targetUrl: '/blog'
  },
  {
    label: 'About',
    targetUrl: '',
    subMenu: [
      {
        label: 'About',
        targetUrl: '/about'
      },
      {
        label: 'Legal Policies',
        targetUrl: '/about/legal-policies'
      }
    ]
  }
]

export default menu

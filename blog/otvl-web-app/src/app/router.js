import { createRouter, createWebHistory } from 'vue-router'
import XPage from '../components/pages/XPage.vue'
import Page from '../components/pages/Page.vue'
import XBlog from '../components/pages/XBlog.vue'
import Blog from '../components/pages/Blog.vue'
import Err404 from '../components/pages/Err404.vue'
import Err5xx from '../components/pages/Err5xx.vue'
import apputils from './apputils.js'

const routes = [
  { path: '/blog', component: XBlog, meta: { isIndex: true } },
  { path: '/blog/:location+', component: Blog },
  { path: '/about', component: XPage, meta: { isIndex: true } },
  { path: '/about/:location+', component:Page },
  { path: '/err404', component: Err404, meta: { isLocal: true } },
  { path: '/err5xx', component: Err5xx, meta: { isLocal: true } },
  { path: '/', redirect: '/blog' },
  { path: '/:pathMatch(.*)*', component: Err404, meta: { isLocal: true } }
]

const router = createRouter({

  history: createWebHistory(),

  routes: routes,

  scrollBehavior(to, from, savedPosition) {
    apputils.scrollBehavior(to, from, savedPosition)
  }

})

export default router

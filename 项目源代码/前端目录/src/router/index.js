import { createWebHistory, createRouter } from 'vue-router'
/* Layout */
import Layout from '@/layout'

/**
 * Note: 路由配置项
 *
 * hidden: true                     // 当设置 true 的时候该路由不会再侧边栏出现 如401，login等页面，或者如一些编辑页面/edit/1
 * alwaysShow: true                 // 当你一个路由下面的 children 声明的路由大于1个时，自动会变成嵌套的模式--如组件页面
 *                                  // 只有一个时，会将那个子路由当做根路由显示在侧边栏--如引导页面
 *                                  // 若你想不管路由下面的 children 声明的个数都显示你的根路由
 *                                  // 你可以设置 alwaysShow: true，这样它就会忽略之前定义的规则，一直显示根路由
 * redirect: noRedirect             // 当设置 noRedirect 的时候该路由在面包屑导航中不可被点击
 * name:'router-name'               // 设定路由的名字，一定要填写不然使用<keep-alive>时会出现各种问题
 * query: '{"id": 1, "name": "ry"}' // 访问路由的默认传递参数
 * roles: ['admin', 'common']       // 访问路由的角色权限
 * permissions: ['a:a:a', 'b:b:b']  // 访问路由的菜单权限
 * meta : {
    noCache: true                   // 如果设置为true，则不会被 <keep-alive> 缓存(默认 false)
    title: 'title'                  // 设置该路由在侧边栏和面包屑中展示的名字
    icon: 'svg-name'                // 设置该路由的图标，对应路径src/assets/icons/svg
    breadcrumb: false               // 如果设置为false，则不会在breadcrumb面包屑中显示
    activeMenu: '/system/user'      // 当路由设置了该属性，则会高亮相对应的侧边栏。
  }
 */

// 公共路由
export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect/index.vue')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error/401'),
    hidden: true
  },
  {
    path: '',
    component: Layout,
    redirect: '/index',
    children: [
      {
        path: '/index',
        component: () => import('@/views/dashboard/index'),
        name: 'Index',
        meta: { title: '首页', icon: 'dashboard', affix: true }
      }
    ]
  },
  {
    path: '/user',
    component: Layout,
    hidden: true,
    redirect: 'noredirect',
    children: [
      {
        path: 'profile/:activeTab?',
        component: () => import('@/views/system/user/profile/index'),
        name: 'Profile',
        meta: { title: '个人中心', icon: 'user' }
      }
    ]
  }
]

// 动态路由，基于用户权限动态去加载
// roles: ['admin'] 表示仅超级管理员角色可见，用于前端双重权限校验
export const dynamicRoutes = [
  {
    path: '/canteen',
    component: Layout,
    alwaysShow: true,
    name: 'Canteen',
    roles: ['admin'],
    meta: { title: '食堂管理', icon: 'component' },
    children: [
      {
        path: 'menu',
        component: () => import('@/views/canteen/menu'),
        name: 'CanteenMenu',
        roles: ['admin'],
        meta: { title: '菜品管理', icon: 'list' }
      },
      {
        path: 'order',
        component: () => import('@/views/canteen/order'),
        name: 'CanteenOrder',
        roles: ['admin'],
        meta: { title: '订单管理', icon: 'shopping' }
      },
      {
        path: 'table',
        component: () => import('@/views/canteen/table'),
        name: 'CanteenTable',
        roles: ['admin'],
        meta: { title: '餐桌管理', icon: 'table' }
      },
      {
        path: 'hr',
        component: Layout,
        alwaysShow: true,
        name: 'HRManage',
        roles: ['admin'],
        meta: { title: '人事管理', icon: 'peoples' },
        children: [
          {
            path: 'staff',
            component: () => import('@/views/canteen/staff'),
            name: 'StaffManage',
            roles: ['admin'],
            meta: { title: '员工管理', icon: 'peoples' }
          }
        ]
      },
      {
        path: 'inventory',
        component: () => import('@/views/canteen/inventory'),
        name: 'CanteenInventory',
        roles: ['admin'],
        meta: { title: '库存管理', icon: 'shopping' }
      },
      {
        path: 'revenue',
        component: () => import('@/views/canteen/revenue'),
        name: 'CanteenRevenue',
        roles: ['admin'],
        meta: { title: '收支管理', icon: 'money' }
      },
      {
        path: 'user',
        component: Layout,
        alwaysShow: true,
        name: 'UserManage',
        roles: ['admin'],
        meta: { title: '用户管理', icon: 'user' },
        children: [
          {
            path: 'list',
            component: () => import('@/views/canteen/user-manage'),
            name: 'UserList',
            roles: ['admin'],
            meta: { title: '用户列表', icon: 'list' }
          },
          {
            path: 'online',
            component: () => import('@/views/canteen/online-users'),
            name: 'OnlineUsers',
            roles: ['admin'],
            meta: { title: '在线用户', icon: 'monitor' }
          }
        ]
      }
    ]
  },
  {
    path: '/order-online',
    component: Layout,
    hidden: false,
    redirect: 'noRedirect',
    name: 'OrderOnline',
    meta: { title: '线上点单', icon: 'shopping-cart' },
    children: [
      {
        path: 'index',
        component: () => import('@/views/canteen/order-online'),
        name: 'OrderOnlineIndex',
        meta: { title: '线上点单', icon: 'shopping-cart' }
      }
    ]
  },
  {
    path: '/visualization',
    component: Layout,
    alwaysShow: true,
    name: 'Visualization',
    roles: ['admin'],
    meta: { title: '数据可视化', icon: 'chart' },
    children: [
      {
        path: 'canteen-sales',
        component: () => import('@/views/visualization/canteen-sales'),
        name: 'CanteenSalesViz',
        roles: ['admin'],
        meta: { title: '食堂销售看板', icon: 'chart' }
      },
      {
        path: 'log-analysis',
        component: () => import('@/views/visualization/log-analysis'),
        name: 'LogAnalysisViz',
        roles: ['admin'],
        meta: { title: '系统日志监控', icon: 'log' }
      },
      {
        path: 'user-analysis',
        component: () => import('@/views/visualization/user-analysis'),
        name: 'UserAnalysisViz',
        roles: ['admin'],
        meta: { title: '用户与部门分析', icon: 'user' }
      },
      {
        path: 'inventory',
        component: () => import('@/views/visualization/inventory'),
        name: 'InventoryViz',
        roles: ['admin'],
        meta: { title: '库存管理看板', icon: 'shopping' }
      },
      {
        path: 'income-expense',
        component: () => import('@/views/visualization/income-expense'),
        name: 'IncomeExpenseViz',
        roles: ['admin'],
        meta: { title: '收支管理看板', icon: 'money' }
      }
    ]
  },
  {
    path: '/ai-chat',
    component: Layout,
    hidden: false,
    redirect: 'noRedirect',
    name: 'CanteenAgent',
    meta: { title: '食堂智能助手', icon: 'ai-chat' },
    children: [
      {
        path: 'canteen-agent',
        component: () => import('@/views/canteen/agent'),
        name: 'CanteenAgentPage',
        meta: { title: '食堂智能助手', icon: 'ai-chat' }
      }
    ]
  },
  {
    path: '/tool',
    component: Layout,
    alwaysShow: true,
    name: 'Tool',
    roles: ['admin'],
    meta: { title: '系统工具', icon: 'tool' },
    children: [
      {
        path: 'swagger',
        component: () => import('@/views/tool/swagger/index.vue'),
        name: 'Swagger',
        roles: ['admin'],
        meta: { title: '系统接口', icon: 'swagger' }
      },
      {
        path: 'build',
        component: () => import('@/views/tool/build/index.vue'),
        name: 'Build',
        roles: ['admin'],
        meta: { title: '表单设计', icon: 'build' }
      },
      {
        path: 'gen',
        component: () => import('@/views/tool/gen/index.vue'),
        name: 'Gen',
        roles: ['admin'],
        meta: { title: '表单构建', icon: 'build' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
});

export default router;

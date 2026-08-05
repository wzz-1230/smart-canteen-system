import auth from '@/plugins/auth'
import router, { constantRoutes, dynamicRoutes } from '@/router'
import { getRouters } from '@/api/menu'
import Layout from '@/layout/index'
import ParentView from '@/components/ParentView'
import InnerLink from '@/layout/components/InnerLink'

// 匹配views里面所有的.vue文件
const modules = import.meta.glob('./../../views/**/*.vue')

const usePermissionStore = defineStore(
  'permission',
  {
    state: () => ({
      routes: [],
      addRoutes: [],
      defaultRoutes: [],
      topbarRouters: [],
      sidebarRouters: []
    }),
    actions: {
      setRoutes(routes) {
        this.addRoutes = routes
        this.routes = constantRoutes.concat(routes)
      },
      setDefaultRoutes(routes) {
        this.defaultRoutes = constantRoutes.concat(routes)
      },
      setTopbarRoutes(routes) {
        this.topbarRouters = routes
      },
      setSidebarRouters(routes) {
        this.sidebarRouters = routes
      },
      generateRoutes(roles) {
        return new Promise(resolve => {
          getRouters().then(res => {
            const backendRoutes = filterAsyncRouter(res.data)

            // ========== 关键修复：在最顶层一次性处理"食堂智能助手"菜单 ==========
            // 避免在递归函数中修改 children 导致死循环
            processCanteenAgentMenu(backendRoutes)

            // ========== 1. 路由注册：同时添加后端返回的路由
            backendRoutes.forEach(route => { router.addRoute(route) })

            // ========== 2. 路由注册：添加前端定义的 dynamicRoutes（通过权限过滤，确保角色未授权的路由不可访问）
            const filteredDynamicRoutes = filterDynamicRoutes(dynamicRoutes)
            filteredDynamicRoutes.forEach(route => { router.addRoute(route) })

            // ========== 3. 添加404路由（必须在所有动态路由之后添加，确保通配符最后匹配）
            router.addRoute({
              path: '/:pathMatch(.*)*',
              component: () => import('@/views/error/404'),
              hidden: true
            })

            // ========== 4. 菜单数据（关键！只使用后端返回的菜单数据，避免菜单重复）
            // - 菜单数据源只使用 backendRoutes（后端返回的完整菜单结构，避免侧边栏菜单不重复）
            this.setRoutes(backendRoutes)
            this.setSidebarRouters(constantRoutes.concat(backendRoutes))
            this.setDefaultRoutes(backendRoutes)
            this.setTopbarRoutes(backendRoutes)
            resolve(backendRoutes)
          })
        })
      }
    }
  })

// 遍历后台传来的路由字符串，转换为组件对象
function filterAsyncRouter(asyncRouterMap, lastRouter = false, type = false) {
  return asyncRouterMap.filter(route => {
    // ========== 修复修复：先处理外链，再做 path 清洗 ==========
    // 1. 先检测是否为外链（http/https 开头），在清洗之前检测
    //   避免 .replace(/\/+/g, '/') 把 http:// 变成 http:/
    let isOuterLink = false
    let originalUrl = ''
    if (route.path) {
      const pathStr = String(route.path).trim().replace(/^[`'"]+|[`'"]+$/g, '')
      if (pathStr.startsWith('http://') || pathStr.startsWith('https://')) {
        isOuterLink = true
        originalUrl = pathStr
      }
    }

    // 2. 如果是外链：转换为 vue-router 能接受的路径格式
    if (isOuterLink) {
      // 将外链路径转换为内部路径（vue-router 要求路径以 / 开头）
      const urlPart = originalUrl.replace(/^https?:\/\//, '').replace(/[^\w-]/g, '-')
      route.path = '/inner-link/' + urlPart
      // 使用 InnerLink 组件承载外链
      route.component = InnerLink
      if (!route.meta) route.meta = {}
      route.meta.link = originalUrl
      // 外链不需要 name（避免与其他路由同名冲突）
      if (route.name) delete route.name
    } else if (route.path) {
      // 3. 普通路径清洗：去除引号和首尾空白；规范化连续斜杠
      route.path = String(route.path).trim()
        .replace(/^[`'"]+|[`'"]+$/g, '')
        .replace(/\/+/g, '/')  // 处理 //canteen 这样的连续斜杠
      // 如果清洗后变空，则回退到基于路由 path 的兜底路径
      if (!route.path) route.path = '/'
    }

    // 4. 清洗 name：过滤空字符串、引号字符串、null、undefined、URL-like name
    // 避免 Vue Router 抛 "A route named '' has been added as a child of a route with the same name"
    function _isBadName(n) {
      if (n === null || n === undefined) return true
      const s = String(n).trim()
      if (s === '' || s === "''" || s === '""' || s.toLowerCase() === 'null') return true
      if (/^https?:\/\//i.test(s)) return true
      return false
    }
    if (_isBadName(route.name)) {
      delete route.name
    }

    // ========== 简化处理：只做 component 替换，不在递归中处理 children ==========
    // 避免修改 children 导致死循环。children 的处理移到最顶层的 processCanteenAgentMenu 函数中
    
    // 如果是旧的 AI对话 子菜单（component 是 ai/chat/index），直接替换为食堂智能助手
    if (route.component && String(route.component).includes('ai/chat')) {
      // 替换组件为食堂智能助手
      route.component = 'canteen/agent/index'
      // 修改菜单名称为食堂智能助手
      if (!route.meta) route.meta = {}
      route.meta.title = '食堂智能助手'
      // 修改 path 为 canteen-agent
      route.path = 'canteen-agent'
    }
    
    // 如果路径包含 ai-chat 或是 AI对话父菜单，修改名称（但不改 children）
    const isAiChatParent = (
      (route.path && String(route.path).includes('ai-chat')) ||
      (route.meta && route.meta.title && (
        String(route.meta.title).includes('AI 对话') || 
        String(route.meta.title).includes('食堂智能助手') ||
        String(route.meta.title).includes('AI对话')
      ))
    )
    if (isAiChatParent && route.children === undefined) {
      // 只有没有 children 的情况下才修改名称
      if (!route.meta) route.meta = {}
      route.meta.title = '食堂智能助手'
    }

    if (type && route.children) {
      route.children = filterChildren(route.children)
    }
    if (route.component) {
      // Layout ParentView 组件特殊处理
      if (route.component === 'Layout') {
        route.component = Layout
      } else if (route.component === 'ParentView') {
        route.component = ParentView
      } else if (route.component === 'InnerLink') {
        route.component = InnerLink
      } else if (typeof route.component === 'string') {
        // 只有当 component 是字符串时才调用 loadView
        route.component = loadView(route.component)
      }
      // 如果 component 不是字符串（如已是组件对象），保持原样
    }
    if (route.children != null && route.children && route.children.length) {
      route.children = filterAsyncRouter(route.children, route, type)
    } else {
      delete route['children']
      delete route['redirect']
    }
    return true
  })
}

function filterChildren(childrenMap, lastRouter = false) {
  var children = []
  childrenMap.forEach(el => {
    // ========== 修复：先检测并处理外链，再做路径清洗 ==========
    // 1. 先检测是否为外链（在清洗之前检测），避免 .replace(/\/+/g, '/') 把 http:// 变成 http:/
    let isOuterLink = false
    let originalUrl = ''
    if (el.path) {
      const pathStr = String(el.path).trim().replace(/^[`'"]+|[`'"]+$/g, '')
      if (pathStr.startsWith('http://') || pathStr.startsWith('https://')) {
        isOuterLink = true
        originalUrl = pathStr
      }
    }

    // 2. 如果是外链：转换为 vue-router 能接受的路径格式
    if (isOuterLink) {
      const urlPart = originalUrl.replace(/^https?:\/\//, '').replace(/[^\w-]/g, '-')
      el.path = '/inner-link/' + urlPart
      el.component = InnerLink
      if (!el.meta) el.meta = {}
      el.meta.link = originalUrl
      if (el.name) delete el.name
    } else if (el.path) {
      // 3. 普通路径清洗：去除首尾引号/空白，并规范化连续斜杠
      el.path = String(el.path).trim()
        .replace(/^[`'"]+|[`'"]+$/g, '')
        .replace(/\/+/g, '/')
    }

    // 4. 清洗子路由的 name：同 filterAsyncRouter 的逻辑
    function _isBadName(n) {
      if (n === null || n === undefined) return true
      const s = String(n).trim()
      if (s === '' || s === "''" || s === '""' || s.toLowerCase() === 'null') return true
      if (/^https?:\/\//i.test(s)) return true
      return false
    }
    if (_isBadName(el.name)) delete el.name

    // ========== 简化处理：子路由中只做 component 替换，不处理 children ==========
    
    // 如果是旧的 AI对话 子菜单（component 是 ai/chat），直接替换为食堂智能助手
    if (el.component && String(el.component).includes('ai/chat')) {
      el.component = 'canteen/agent/index'
      if (!el.meta) el.meta = {}
      el.meta.title = '食堂智能助手'
      // 修改 path 为 canteen-agent
      el.path = 'canteen-agent'
    }
    
    // 如果路径包含 ai-chat 或是 AI对话父菜单，修改名称（但不改 children）
    const isAiChild = (
      (el.path && String(el.path).includes('ai-chat')) ||
      (el.meta && el.meta.title && (
        String(el.meta.title).includes('AI 对话') || 
        String(el.meta.title).includes('食堂智能助手') ||
        String(el.meta.title).includes('AI对话')
      ))
    )
    if (isAiChild && el.children === undefined) {
      if (!el.meta) el.meta = {}
      el.meta.title = '食堂智能助手'
    }

    el.path = lastRouter ? lastRouter.path + '/' + el.path : el.path
    if (el.children && el.children.length && el.component === 'ParentView') {
      children = children.concat(filterChildren(el.children, el))
    } else {
      children.push(el)
    }
  })
  return children
}

// 动态路由遍历，验证是否具备权限
export function filterDynamicRoutes(routes) {
  const res = []
  routes.forEach(route => {
    if (route.permissions) {
      if (auth.hasPermiOr(route.permissions)) {
        res.push(route)
      }
    } else if (route.roles) {
      if (auth.hasRoleOr(route.roles)) {
        res.push(route)
      }
    } else {
      // 如果没有配置权限检查，直接添加路由
      res.push(route)
    }
  })
  return res
}

export const loadView = (view) => {
  // 类型安全检查：确保 view 是有效的非空字符串
  if (view === null || view === undefined) return undefined;
  if (typeof view !== 'string') return undefined;
  const viewStr = String(view).trim();
  if (viewStr === '') return undefined;
  
  let res;
  
  // 第1层：尝试精确匹配
  for (const path in modules) {
    const dir = path.split('views/')[1].split('.vue')[0];
    if (dir === viewStr) {
      res = () => modules[path]();
      return res;
    }
  }
  
  // 第2层：如果没找到，尝试添加 /index（处理目录型组件如 canteen/inventory → canteen/inventory/index）
  if (res === undefined) {
    const viewWithIndex = viewStr.endsWith('/index') ? viewStr : viewStr + '/index';
    for (const path in modules) {
      const dir = path.split('views/')[1].split('.vue')[0];
      if (dir === viewWithIndex) {
        res = () => modules[path]();
        return res;
      }
    }
  }
  
  // 第3层：最后兜底：查找包含该路径的任何 .vue 文件
  if (res === undefined) {
    for (const path in modules) {
      const dir = path.split('views/')[1].split('.vue')[0];
      if (dir.startsWith(viewStr + '/') || 
          dir.startsWith(viewStr.replace(/\/index$/, '') + '/')) {
        res = () => modules[path]();
        return res;
      }
    }
  }
  return res;
}

// ========== 关键函数：在最顶层一次性处理"食堂智能助手"菜单
// 避免在递归函数中修改 children 导致死循环
function processCanteenAgentMenu(routes) {
  if (!routes || !Array.isArray(routes) || routes.length === 0) return
  
  for (let i = 0; i < routes.length; i++) {
    const route = routes[i]
    if (!route) continue
    
    // 检查是否是"AI对话"或"食堂智能助手"父菜单
    const pathStr = String(route.path || '')
    const titleStr = String((route.meta && route.meta.title) || '')
    const isCanteenAgentParent = 
      pathStr.includes('ai-chat') ||
      titleStr.includes('AI 对话') ||
      titleStr.includes('AI对话') ||
      titleStr.includes('食堂智能助手')
    
    if (isCanteenAgentParent) {
      // 修改父菜单名称
      if (!route.meta) route.meta = {}
      route.meta.title = '食堂智能助手'
      
      // 关键：替换整个 children 数组，只保留指向食堂智能助手的那一个
      // 同时避免递归处理导致死循环
      route.children = [{
        path: 'canteen-agent',
        component: loadView('canteen/agent/index'),
        name: 'CanteenAgent',
        meta: { title: '食堂智能助手', icon: 'ai-chat' }
      }]
      
      // 设置重定向到子路由
      route.redirect = '/ai-chat/canteen-agent'
    }
  }
}

export default usePermissionStore

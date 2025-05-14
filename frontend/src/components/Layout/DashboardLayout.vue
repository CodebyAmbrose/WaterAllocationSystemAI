<template>
  <div class="dashboard-layout h-screen flex flex-col md:flex-row overflow-hidden w-full">
    <!-- Mobile header -->
    <div class="md:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between w-full">
      <div class="flex items-center">
        <button @click="toggleMobileMenu" class="mr-2 text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
          </svg>
        </button>
        <span class="font-bold text-lg text-gray-900">WaterAlloc</span>
      </div>
      <div class="flex items-center">
        <div class="relative">
          <div class="bg-green-100 text-green-800 px-2 py-0.5 text-xs rounded-full flex items-center">
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-green-500 mr-1"></span>
            Connected
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile menu overlay -->
    <div v-if="mobileMenuOpen" class="md:hidden fixed inset-0 bg-gray-600 bg-opacity-75 z-20" @click="toggleMobileMenu"></div>

    <!-- Sidebar -->
    <div 
      class="sidebar bg-gradient-to-b from-gray-900 to-gray-800 text-white w-64 md:w-64 flex-shrink-0 transition-all duration-300 ease-in-out z-30 fixed md:relative inset-y-0 left-0 transform"
      :class="{ 
        'translate-x-0': mobileMenuOpen,
        '-translate-x-full': !mobileMenuOpen && !isDesktop,
        'md:translate-x-0': isDesktop,
        'w-20 md:w-20': collapsed && isDesktop
      }"
    >
      <!-- Logo area -->
      <div class="p-4 flex items-center justify-between h-16 border-b border-gray-700/50">
        <div class="flex items-center">
          <div class="text-blue-400 w-8 h-8">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.29 15.88L13.17 12 9.29 8.12c-.39-.39-.39-1.02 0-1.41.39-.39 1.02-.39 1.41 0l4.59 4.59c.39.39.39 1.02 0 1.41L10.7 17.3c-.39.39-1.02.39-1.41 0-.38-.39-.39-1.03 0-1.42z"/>
            </svg>
          </div>
          <span v-if="!collapsed || !isDesktop" class="ml-2 font-bold text-lg">WaterAlloc</span>
        </div>
        <div class="flex">
          <button @click="toggleMobileMenu" class="md:hidden text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <button @click="toggleSidebar" class="hidden md:block text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Nav links -->
      <div class="py-4 overflow-y-auto h-full">
        <nav class="mt-5 px-3">
          <div v-for="(item, index) in navItems" :key="index" class="mb-2">
            <button 
              @click="handleNavClick(item.id)"
              class="flex items-center px-4 py-3 w-full text-left rounded-lg transition-all duration-200"
              :class="activeTab === item.id 
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-md' 
                : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'"
            >
              <span class="text-lg" v-html="item.icon"></span>
              <span v-if="!collapsed || !isDesktop" class="ml-3 font-medium">{{ item.name }}</span>
              <span v-if="activeTab === item.id && (!collapsed || !isDesktop)" class="ml-auto bg-blue-200/20 rounded-full p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </span>
            </button>
          </div>
        </nav>
      </div>
      
      <!-- User area -->
      <div class="mt-auto border-t border-gray-700/50 p-4 flex items-center" v-if="!collapsed || !isDesktop">
        <div class="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
          <span class="text-white font-medium">{{ userInitials }}</span>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-white">Water Admin</p>
          <p class="text-xs text-blue-200">AI-Powered System</p>
        </div>
      </div>
    </div>
    
    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden bg-gray-50 w-full">
      <!-- Top navigation (desktop) -->
      <header class="bg-white shadow-sm h-16 hidden md:flex items-center justify-between px-6 z-10 w-full">
        <div class="flex items-center">
          <h1 class="text-xl font-semibold text-gray-800">{{ getCurrentPageTitle }}</h1>
        </div>
        <div class="flex items-center space-x-4">
          <div class="relative">
            <div class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center shadow-sm">
              <span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
              BSC Testnet Connected
            </div>
          </div>
          <button class="p-1 text-gray-500 hover:text-gray-700 focus:outline-none relative">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 text-xs flex items-center justify-center">3</span>
          </button>
        </div>
      </header>
      
      <!-- Main content area -->
      <main class="flex-1 overflow-y-auto p-4 md:p-6 w-full">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardLayout',
  props: {
    activeTab: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      collapsed: false,
      mobileMenuOpen: false,
      isDesktop: false,
      navItems: [
        { 
          id: 'dashboard', 
          name: 'Dashboard', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>' 
        },
        { 
          id: 'predict', 
          name: 'Generate Predictions', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" /></svg>' 
        },
        { 
          id: 'approve', 
          name: 'Stakeholder Approval', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' 
        },
        { 
          id: 'history', 
          name: 'Prediction History', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' 
        },
        { 
          id: 'analytics', 
          name: 'Analytics', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' 
        },
        { 
          id: 'settings', 
          name: 'Settings', 
          icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>' 
        },
      ]
    };
  },
  computed: {
    userInitials() {
      return 'WA';
    },
    getCurrentPageTitle() {
      const currentPage = this.navItems.find(item => item.id === this.activeTab);
      return currentPage ? currentPage.name : 'Dashboard';
    }
  },
  mounted() {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  },
  methods: {
    toggleSidebar() {
      this.collapsed = !this.collapsed;
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
    handleNavClick(tabId) {
      this.$emit('change-tab', tabId);
      if (!this.isDesktop) {
        this.mobileMenuOpen = false;
      }
    },
    checkScreenSize() {
      this.isDesktop = window.innerWidth >= 768; // md breakpoint
      if (this.isDesktop) {
        this.mobileMenuOpen = false;
      }
    }
  }
};
</script>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
  width: 100vw;
  max-width: 100%;
}

.sidebar {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.sidebar button {
  transition: all 0.2s ease;
}

.sidebar button:hover {
  transform: translateX(4px);
}
</style> 
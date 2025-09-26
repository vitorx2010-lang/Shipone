import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Menu, Package, Truck, Users, BarChart3, Settings, LogOut } from 'lucide-react'

const Layout = ({ children, currentUser, onLogout }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Envios', href: '/shipments', icon: Package },
    { name: 'Rastreamento', href: '/tracking', icon: Truck },
    { name: 'Usuários', href: '/users', icon: Users, adminOnly: true },
    { name: 'Configurações', href: '/settings', icon: Settings },
  ]

  const filteredNavigation = navigation.filter(item => 
    !item.adminOnly || (currentUser && currentUser.role === 'admin')
  )

  const NavItems = ({ mobile = false }) => (
    <nav className={`${mobile ? 'flex flex-col space-y-2' : 'hidden md:flex md:space-x-8'}`}>
      {filteredNavigation.map((item) => {
        const Icon = item.icon
        return (
            <a
              key={item.name}
              href={`#${item.href.slice(1)}`}
              className={`${
                mobile 
                  ? 'flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                  : 'flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50'
              } transition-colors duration-200`}
              onClick={() => mobile && setIsMobileMenuOpen(false)}
            >
            <Icon className={`${mobile ? 'mr-3 h-5 w-5' : 'mr-2 h-4 w-4'}`} />
            {item.name}
          </a>
        )
      })}
    </nav>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Package className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">ShipOne</span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <NavItems />

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {currentUser && (
                <div className="hidden md:flex items-center space-x-4">
                  <span className="text-sm text-gray-700">
                    Olá, {currentUser.full_name || currentUser.username}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onLogout}
                    className="text-gray-700 hover:text-red-600"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Sair
                  </Button>
                </div>
              )}

              {/* Mobile menu button */}
              <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm" className="md:hidden">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-64">
                  <div className="flex flex-col h-full">
                    <div className="flex items-center mb-8">
                      <Package className="h-8 w-8 text-blue-600" />
                      <span className="ml-2 text-xl font-bold text-gray-900">ShipOne</span>
                    </div>
                    
                    <NavItems mobile />
                    
                    {currentUser && (
                      <div className="mt-auto pt-6 border-t">
                        <div className="mb-4">
                          <p className="text-sm font-medium text-gray-900">
                            {currentUser.full_name || currentUser.username}
                          </p>
                          <p className="text-sm text-gray-500">{currentUser.email}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            onLogout()
                            setIsMobileMenuOpen(false)
                          }}
                          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <LogOut className="h-4 w-4 mr-2" />
                          Sair
                        </Button>
                      </div>
                    )}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

export default Layout


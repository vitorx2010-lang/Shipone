import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Package, Plus, Search, Truck, MapPin, Calendar, Weight } from 'lucide-react'

const Shipments = ({ token }) => {
  const [shipments, setShipments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [newShipment, setNewShipment] = useState({
    recipient_name: '',
    recipient_email: '',
    recipient_phone: '',
    origin_address: '',
    destination_address: '',
    origin_city: '',
    destination_city: '',
    origin_country: '',
    destination_country: '',
    weight: '',
    dimensions: '',
    package_type: '',
    service_type: '',
    cost: '',
    currency: 'USD'
  })

  useEffect(() => {
    fetchShipments()
  }, [])

  const fetchShipments = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/logistics/shipments', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setShipments(data.shipments)
      }
    } catch (error) {
      console.error('Erro ao buscar envios:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateShipment = async (e) => {
    e.preventDefault()
    setCreateLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('http://localhost:5000/api/logistics/shipments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...newShipment,
          weight: parseFloat(newShipment.weight),
          cost: newShipment.cost ? parseFloat(newShipment.cost) : undefined
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess('Envio criado com sucesso!')
        setNewShipment({
          recipient_name: '',
          recipient_email: '',
          recipient_phone: '',
          origin_address: '',
          destination_address: '',
          origin_city: '',
          destination_city: '',
          origin_country: '',
          destination_country: '',
          weight: '',
          dimensions: '',
          package_type: '',
          service_type: '',
          cost: '',
          currency: 'USD'
        })
        fetchShipments()
        setTimeout(() => {
          setIsCreateDialogOpen(false)
          setSuccess('')
        }, 2000)
      } else {
        setError(data.message || 'Erro ao criar envio')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setCreateLoading(false)
    }
  }

  const handleInputChange = (field, value) => {
    setNewShipment(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_transit: 'bg-blue-100 text-blue-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusText = (status) => {
    const texts = {
      pending: 'Pendente',
      in_transit: 'Em Trânsito',
      delivered: 'Entregue',
      cancelled: 'Cancelado'
    }
    return texts[status] || status
  }

  const getServiceTypeText = (type) => {
    const texts = {
      standard: 'Padrão',
      express: 'Expresso',
      overnight: 'Overnight'
    }
    return texts[type] || type
  }

  const filteredShipments = shipments.filter(shipment =>
    shipment.tracking_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    shipment.recipient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    shipment.destination_city.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Envios</h1>
        </div>
        <div className="grid gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Envios</h1>
          <p className="text-gray-600 mt-2">Gerencie seus envios e rastreamentos</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Novo Envio
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Criar Novo Envio</DialogTitle>
              <DialogDescription>
                Preencha os dados para criar um novo envio
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateShipment} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              {success && (
                <Alert>
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              )}

              {/* Destinatário */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Destinatário</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="recipient_name">Nome *</Label>
                    <Input
                      id="recipient_name"
                      required
                      value={newShipment.recipient_name}
                      onChange={(e) => handleInputChange('recipient_name', e.target.value)}
                      placeholder="Nome do destinatário"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="recipient_email">Email</Label>
                    <Input
                      id="recipient_email"
                      type="email"
                      value={newShipment.recipient_email}
                      onChange={(e) => handleInputChange('recipient_email', e.target.value)}
                      placeholder="email@exemplo.com"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="recipient_phone">Telefone</Label>
                  <Input
                    id="recipient_phone"
                    value={newShipment.recipient_phone}
                    onChange={(e) => handleInputChange('recipient_phone', e.target.value)}
                    placeholder="(11) 99999-9999"
                  />
                </div>
              </div>

              {/* Endereços */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Endereços</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="origin_address">Endereço de Origem *</Label>
                    <Textarea
                      id="origin_address"
                      required
                      value={newShipment.origin_address}
                      onChange={(e) => handleInputChange('origin_address', e.target.value)}
                      placeholder="Endereço completo de origem"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="destination_address">Endereço de Destino *</Label>
                    <Textarea
                      id="destination_address"
                      required
                      value={newShipment.destination_address}
                      onChange={(e) => handleInputChange('destination_address', e.target.value)}
                      placeholder="Endereço completo de destino"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="origin_city">Cidade Origem *</Label>
                    <Input
                      id="origin_city"
                      required
                      value={newShipment.origin_city}
                      onChange={(e) => handleInputChange('origin_city', e.target.value)}
                      placeholder="São Paulo"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="destination_city">Cidade Destino *</Label>
                    <Input
                      id="destination_city"
                      required
                      value={newShipment.destination_city}
                      onChange={(e) => handleInputChange('destination_city', e.target.value)}
                      placeholder="Rio de Janeiro"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="origin_country">País Origem *</Label>
                    <Input
                      id="origin_country"
                      required
                      value={newShipment.origin_country}
                      onChange={(e) => handleInputChange('origin_country', e.target.value)}
                      placeholder="Brasil"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="destination_country">País Destino *</Label>
                    <Input
                      id="destination_country"
                      required
                      value={newShipment.destination_country}
                      onChange={(e) => handleInputChange('destination_country', e.target.value)}
                      placeholder="Brasil"
                    />
                  </div>
                </div>
              </div>

              {/* Detalhes do Pacote */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Detalhes do Pacote</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="weight">Peso (kg) *</Label>
                    <Input
                      id="weight"
                      type="number"
                      step="0.1"
                      required
                      value={newShipment.weight}
                      onChange={(e) => handleInputChange('weight', e.target.value)}
                      placeholder="1.5"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dimensions">Dimensões (LxWxH cm)</Label>
                    <Input
                      id="dimensions"
                      value={newShipment.dimensions}
                      onChange={(e) => handleInputChange('dimensions', e.target.value)}
                      placeholder="30x20x10"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="package_type">Tipo de Pacote *</Label>
                    <Select value={newShipment.package_type} onValueChange={(value) => handleInputChange('package_type', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="box">Caixa</SelectItem>
                        <SelectItem value="envelope">Envelope</SelectItem>
                        <SelectItem value="pallet">Pallet</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="service_type">Tipo de Serviço *</Label>
                    <Select value={newShipment.service_type} onValueChange={(value) => handleInputChange('service_type', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o serviço" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard">Padrão (7 dias)</SelectItem>
                        <SelectItem value="express">Expresso (3 dias)</SelectItem>
                        <SelectItem value="overnight">Overnight (1 dia)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cost">Custo</Label>
                    <Input
                      id="cost"
                      type="number"
                      step="0.01"
                      value={newShipment.cost}
                      onChange={(e) => handleInputChange('cost', e.target.value)}
                      placeholder="100.00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="currency">Moeda</Label>
                    <Select value={newShipment.currency} onValueChange={(value) => handleInputChange('currency', value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="BRL">BRL</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={createLoading}>
                  {createLoading ? 'Criando...' : 'Criar Envio'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-2">
        <Search className="h-4 w-4 text-gray-400" />
        <Input
          placeholder="Buscar por número de rastreamento, destinatário ou cidade..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-md"
        />
      </div>

      {/* Shipments List */}
      <div className="space-y-4">
        {filteredShipments.length > 0 ? (
          filteredShipments.map((shipment) => (
            <Card key={shipment.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <Package className="h-8 w-8 text-gray-400 mt-1" />
                    <div className="space-y-2">
                      <div>
                        <h3 className="font-semibold text-lg">{shipment.tracking_number}</h3>
                        <p className="text-gray-600">Para: {shipment.recipient_name}</p>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {shipment.origin_city} → {shipment.destination_city}
                        </div>
                        <div className="flex items-center">
                          <Weight className="h-4 w-4 mr-1" />
                          {shipment.weight} kg
                        </div>
                        <div className="flex items-center">
                          <Truck className="h-4 w-4 mr-1" />
                          {getServiceTypeText(shipment.service_type)}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(shipment.created_at).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                      {shipment.estimated_delivery && (
                        <p className="text-sm text-gray-500">
                          Entrega estimada: {new Date(shipment.estimated_delivery).toLocaleDateString('pt-BR')}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={getStatusColor(shipment.status)}>
                      {getStatusText(shipment.status)}
                    </Badge>
                    {shipment.cost && (
                      <p className="text-sm text-gray-500 mt-2">
                        {shipment.currency} {shipment.cost}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum envio encontrado</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm ? 'Tente ajustar sua busca' : 'Comece criando seu primeiro envio'}
              </p>
              {!searchTerm && (
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Criar Primeiro Envio
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default Shipments


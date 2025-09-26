import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Search, Package, MapPin, Calendar, Truck, CheckCircle, Clock, AlertCircle } from 'lucide-react'

const Tracking = () => {
  const [trackingNumber, setTrackingNumber] = useState('')
  const [shipmentData, setShipmentData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTrack = async (e) => {
    e.preventDefault()
    if (!trackingNumber.trim()) return

    setLoading(true)
    setError('')
    setShipmentData(null)

    try {
      const response = await fetch(`http://localhost:5000/api/logistics/shipments/${trackingNumber}`)
      
      if (response.ok) {
        const data = await response.json()
        setShipmentData(data.shipment)
      } else {
        const errorData = await response.json()
        setError(errorData.message || 'Envio não encontrado')
      }
    } catch (err) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_transit: 'bg-blue-100 text-blue-800',
      out_for_delivery: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusText = (status) => {
    const texts = {
      pending: 'Pendente',
      in_transit: 'Em Trânsito',
      out_for_delivery: 'Saiu para Entrega',
      delivered: 'Entregue',
      cancelled: 'Cancelado'
    }
    return texts[status] || status
  }

  const getEventIcon = (eventType) => {
    const icons = {
      created: Clock,
      pickup: Package,
      in_transit: Truck,
      out_for_delivery: MapPin,
      delivered: CheckCircle,
      cancelled: AlertCircle
    }
    return icons[eventType] || Clock
  }

  const getEventColor = (eventType) => {
    const colors = {
      created: 'text-gray-500',
      pickup: 'text-blue-500',
      in_transit: 'text-blue-600',
      out_for_delivery: 'text-purple-600',
      delivered: 'text-green-600',
      cancelled: 'text-red-600'
    }
    return colors[eventType] || 'text-gray-500'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Rastreamento</h1>
        <p className="text-gray-600 mt-2">Acompanhe seus envios em tempo real</p>
      </div>

      {/* Search Form */}
      <Card>
        <CardHeader>
          <CardTitle>Rastrear Envio</CardTitle>
          <CardDescription>
            Digite o número de rastreamento para acompanhar seu envio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleTrack} className="flex space-x-2">
            <div className="flex-1">
              <Input
                placeholder="Digite o número de rastreamento (ex: SHP12345678)"
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
                className="text-lg"
              />
            </div>
            <Button type="submit" disabled={loading} size="lg">
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Search className="h-4 w-4 mr-2" />
              )}
              Rastrear
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Shipment Details */}
      {shipmentData && (
        <div className="space-y-6">
          {/* Shipment Info */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl">{shipmentData.tracking_number}</CardTitle>
                  <CardDescription className="text-lg mt-2">
                    Para: {shipmentData.recipient_name}
                  </CardDescription>
                </div>
                <Badge className={`${getStatusColor(shipmentData.status)} text-lg px-4 py-2`}>
                  {getStatusText(shipmentData.status)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Origem</h4>
                  <p className="text-sm text-gray-600">{shipmentData.origin_city}</p>
                  <p className="text-sm text-gray-600">{shipmentData.origin_country}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Destino</h4>
                  <p className="text-sm text-gray-600">{shipmentData.destination_city}</p>
                  <p className="text-sm text-gray-600">{shipmentData.destination_country}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Peso</h4>
                  <p className="text-sm text-gray-600">{shipmentData.weight} kg</p>
                  {shipmentData.dimensions && (
                    <p className="text-sm text-gray-600">{shipmentData.dimensions} cm</p>
                  )}
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Entrega Estimada</h4>
                  <p className="text-sm text-gray-600">
                    {shipmentData.estimated_delivery 
                      ? new Date(shipmentData.estimated_delivery).toLocaleDateString('pt-BR')
                      : 'Não informado'
                    }
                  </p>
                  {shipmentData.actual_delivery && (
                    <p className="text-sm text-green-600 font-medium">
                      Entregue em: {new Date(shipmentData.actual_delivery).toLocaleDateString('pt-BR')}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tracking Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Rastreamento</CardTitle>
              <CardDescription>
                Acompanhe o progresso do seu envio
              </CardDescription>
            </CardHeader>
            <CardContent>
              {shipmentData.tracking_events && shipmentData.tracking_events.length > 0 ? (
                <div className="space-y-6">
                  {shipmentData.tracking_events
                    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                    .map((event, index) => {
                      const Icon = getEventIcon(event.event_type)
                      const isLatest = index === 0
                      
                      return (
                        <div key={event.id} className="flex items-start space-x-4">
                          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                            isLatest ? 'bg-blue-100' : 'bg-gray-100'
                          }`}>
                            <Icon className={`h-5 w-5 ${
                              isLatest ? 'text-blue-600' : getEventColor(event.event_type)
                            }`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className={`text-sm font-medium ${
                                isLatest ? 'text-blue-900' : 'text-gray-900'
                              }`}>
                                {event.description}
                              </p>
                              <p className="text-sm text-gray-500">
                                {new Date(event.timestamp).toLocaleString('pt-BR')}
                              </p>
                            </div>
                            {event.location && (
                              <p className="text-sm text-gray-600 mt-1">
                                <MapPin className="h-3 w-3 inline mr-1" />
                                {event.location}
                              </p>
                            )}
                          </div>
                        </div>
                      )
                    })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Nenhum evento de rastreamento disponível</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Contact Info */}
          {(shipmentData.recipient_email || shipmentData.recipient_phone) && (
            <Card>
              <CardHeader>
                <CardTitle>Informações de Contato</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {shipmentData.recipient_email && (
                    <p className="text-sm">
                      <span className="font-medium">Email:</span> {shipmentData.recipient_email}
                    </p>
                  )}
                  {shipmentData.recipient_phone && (
                    <p className="text-sm">
                      <span className="font-medium">Telefone:</span> {shipmentData.recipient_phone}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Sample Tracking Numbers */}
      {!shipmentData && !loading && (
        <Card>
          <CardHeader>
            <CardTitle>Números de Rastreamento de Exemplo</CardTitle>
            <CardDescription>
              Use estes números para testar o sistema de rastreamento
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="font-mono text-sm">SHP12345678</p>
                <p className="text-xs text-gray-600 mt-1">Envio em trânsito</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="font-mono text-sm">SHP87654321</p>
                <p className="text-xs text-gray-600 mt-1">Envio entregue</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Tracking


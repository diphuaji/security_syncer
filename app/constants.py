from backtrader.order import Order


STATUS_MAPPING = {
    Order.Created: 'Created',
    Order.Submitted: 'Submitted',
    Order.Accepted: 'Accepted',
    Order.Partial: 'Partial',
    Order.Completed: 'Completed',
    Order.Rejected: 'Rejected',
    Order.Margin: 'Margin',
    Order.Cancelled: 'Cancelled',
}

ORDER_TYPE_MAPPING  = {
    Order.StopLimit: 'StopLimit',
    Order.Close: 'Close',
    Order.Limit: 'Limit',
    Order.Stop: 'Stop',
    Order.Market: 'Market',
}
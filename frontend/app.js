const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    // Splash screen logic
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        splash.style.opacity = '0';
        setTimeout(() => {
            splash.classList.add('hidden');
            document.getElementById('browser-screen').classList.remove('hidden');
            loadStations();
        }, 500);
    }, 3000);
});

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(screenId).classList.remove('hidden');
}

async function loadStations() {
    try {
        const response = await fetch(`${API_BASE_URL}/stations`);
        const stations = await response.json();
        
        const yaoundeGrid = document.getElementById('yaounde-stations');
        const doualaGrid = document.getElementById('douala-stations');
        
        yaoundeGrid.innerHTML = '';
        doualaGrid.innerHTML = '';
        
        stations.forEach(station => {
            const hasStock = station.cylinders.some(c => c.stock_quantity > 0);
            
            const card = document.createElement('div');
            card.className = 'station-card';
            card.onclick = () => openStationDetail(station.id);
            
            card.innerHTML = `
                <div class="station-card-header">
                    <span style="font-size: 1.5rem">⛽</span>
                    <h3>${station.name}</h3>
                </div>
                <div class="station-card-body">
                    <div class="stock-indicator ${hasStock ? 'in-stock' : 'out-of-stock'}"></div>
                    <div class="station-details">
                        <div style="margin-bottom: 0.5rem">📍 ${station.address || 'Address not provided'}</div>
                        <div>📞 ${station.phone || 'Phone not provided'}</div>
                        <div style="margin-top: 1rem; font-weight: 600; color: ${hasStock ? 'var(--success)' : 'var(--muted)'}">
                            ${hasStock ? 'Available' : 'Out of Stock'}
                        </div>
                    </div>
                </div>
            `;
            
            if (station.city === 'Yaounde') {
                yaoundeGrid.appendChild(card);
            } else if (station.city === 'Douala') {
                doualaGrid.appendChild(card);
            }
        });
    } catch (error) {
        console.error('Error loading stations:', error);
        alert('Failed to connect to the backend server.');
    }
}

async function openStationDetail(stationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/stations/${stationId}`);
        const station = await response.json();
        
        document.getElementById('detail-station-name').textContent = station.name;
        document.getElementById('detail-station-address').textContent = `Address: ${station.address || 'N/A'}`;
        document.getElementById('detail-station-phone').textContent = `Phone: ${station.phone || 'N/A'}`;
        
        const tbody = document.getElementById('cylinder-list');
        tbody.innerHTML = '';
        
        station.cylinders.forEach(cyl => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${cyl.size_kg} kg</td>
                <td>${cyl.stock_quantity > 0 ? `<span style="color:var(--success)">${cyl.stock_quantity} in stock</span>` : `<span style="color:var(--muted)">Out of stock</span>`}</td>
                <td>${cyl.price}</td>
                <td>
                    <button class="btn-small" ${cyl.stock_quantity === 0 ? 'disabled' : ''} onclick="prepareOrder(${station.id}, ${cyl.id}, ${cyl.price}, ${cyl.stock_quantity})">Order</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        // Hide order form initially
        document.getElementById('order-form-container').classList.add('hidden');
        
        showScreen('detail-screen');
    } catch (error) {
        console.error('Error loading station details:', error);
    }
}

function prepareOrder(stationId, cylinderId, price, maxQuantity) {
    document.getElementById('order-station-id').value = stationId;
    document.getElementById('order-cylinder-id').value = cylinderId;
    document.getElementById('order-price').value = price;
    
    const qtyInput = document.getElementById('order-quantity');
    qtyInput.value = 1;
    qtyInput.max = maxQuantity;
    
    updateTotal();
    
    document.getElementById('order-form-container').classList.remove('hidden');
    // Scroll to order form
    document.getElementById('order-form-container').scrollIntoView({ behavior: 'smooth' });
}

function updateTotal() {
    const price = parseFloat(document.getElementById('order-price').value) || 0;
    const qty = parseInt(document.getElementById('order-quantity').value) || 1;
    document.getElementById('order-total').textContent = (price * qty).toLocaleString();
}

async function submitOrder(e) {
    e.preventDefault();
    
    const orderData = {
        station_id: parseInt(document.getElementById('order-station-id').value),
        cylinder_id: parseInt(document.getElementById('order-cylinder-id').value),
        quantity: parseInt(document.getElementById('order-quantity').value),
        customer_name: document.getElementById('customer-name').value,
        customer_phone: document.getElementById('customer-phone').value,
        customer_town: document.getElementById('customer-town').value,
        customer_quarter: document.getElementById('customer-quarter').value,
        customer_address: document.getElementById('customer-address').value,
        payment_method: document.getElementById('payment-method').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            const orderRes = await response.json();
            document.getElementById('customer-validation-code').textContent = orderRes.validation_code || "----";
            document.getElementById('success-modal').classList.remove('hidden');
            document.getElementById('order-form').reset();
        } else {
            const err = await response.json();
            alert(`Error placing order: ${err.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Order submission error:', error);
        alert('Failed to submit order. Check your connection.');
    }
}

function closeModal() {
    document.getElementById('success-modal').classList.add('hidden');
    showScreen('browser-screen');
    loadStations(); // Refresh stock
}

// ================= AUTHENTICATION & DASHBOARDS ================= //

let currentUser = null;

function showLoginModal() { document.getElementById('login-modal').classList.remove('hidden'); }
function closeLoginModal() { document.getElementById('login-modal').classList.add('hidden'); }

async function handleLogin(e) {
    e.preventDefault();
    const u = document.getElementById('login-username').value;
    const p = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        if (response.ok) {
            currentUser = await response.json();
            closeLoginModal();
            document.getElementById('login-form').reset();
            if (currentUser.role === 'admin') {
                showScreen('admin-screen');
                loadAdminDashboard();
            } else if (currentUser.role === 'delivery') {
                showScreen('delivery-screen');
                loadDeliveryDashboard();
            }
        } else {
            alert('Invalid credentials');
        }
    } catch (error) {
        console.error('Login error', error);
        alert('Connection error');
    }
}

function logout() {
    currentUser = null;
    showScreen('browser-screen');
}

// ================= ADMIN DASHBOARD ================= //

async function loadAdminDashboard() {
    try {
        const ordersRes = await fetch(`${API_BASE_URL}/orders`);
        const orders = await ordersRes.json();
        
        const staffRes = await fetch(`${API_BASE_URL}/delivery-staff`);
        const staff = await staffRes.json();
        
        const tbody = document.querySelector('#admin-orders-table tbody');
        tbody.innerHTML = '';
        
        orders.forEach(order => {
            const tr = document.createElement('tr');
            let actionHtml = '';
            if (order.status === 'pending') {
                let options = staff.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
                actionHtml = `
                    <select id="assign-staff-${order.id}" style="padding: 0.2rem; border-radius: 4px;">
                        ${options}
                    </select>
                    <button class="btn-small" onclick="assignDelivery(${order.id})">Assign</button>
                `;
            } else if (order.delivery) {
                const assignedStaff = staff.find(s => s.id === order.delivery.delivery_person_id);
                const staffName = assignedStaff ? assignedStaff.name : `ID ${order.delivery.delivery_person_id}`;
                actionHtml = `Assigned to:<br><strong>${staffName}</strong>`;
            }
            
            tr.innerHTML = `
                <td>#${order.id}</td>
                <td>${order.customer_name}<br><small>${order.customer_phone}</small></td>
                <td>${order.station.name}</td>
                <td><span class="badge ${order.status}">${order.status}</span></td>
                <td>${actionHtml}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Admin dashboard error", error);
    }
}

async function assignDelivery(orderId) {
    const staffId = document.getElementById(`assign-staff-${orderId}`).value;
    try {
        const response = await fetch(`${API_BASE_URL}/orders/${orderId}/assign?delivery_person_id=${staffId}`, { method: 'PUT' });
        if (response.ok) {
            loadAdminDashboard();
        } else {
            alert("Failed to assign delivery.");
        }
    } catch (error) {
        console.error("Assignment error", error);
    }
}

// ================= DELIVERY DASHBOARD ================= //

async function loadDeliveryDashboard() {
    if (!currentUser) return;
    try {
        const response = await fetch(`${API_BASE_URL}/deliveries/${currentUser.id}`);
        const orders = await response.json();
        
        const tbody = document.querySelector('#delivery-orders-table tbody');
        tbody.innerHTML = '';
        
        orders.forEach(order => {
            const tr = document.createElement('tr');
            let actionHtml = '';
            if (order.status === 'processing') {
                actionHtml = `<button class="btn-small" style="background:var(--success)" onclick="openDeliveryCodeModal(${order.id})">Verify Code</button>`;
            } else {
                actionHtml = `Done`;
            }
            
            tr.innerHTML = `
                <td>#${order.id}</td>
                <td>${order.customer_name}<br><small>${order.customer_phone}</small></td>
                <td>${order.customer_address || order.customer_quarter || 'N/A'}</td>
                <td><span class="badge ${order.status}">${order.status}</span></td>
                <td>${actionHtml}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Delivery dashboard error", error);
    }
}

function openDeliveryCodeModal(orderId) {
    document.getElementById('delivery-order-id').value = orderId;
    document.getElementById('delivery-validation-code').value = '';
    document.getElementById('delivery-code-modal').classList.remove('hidden');
}

function closeDeliveryCodeModal() {
    document.getElementById('delivery-code-modal').classList.add('hidden');
}

async function handleCompleteDelivery(e) {
    e.preventDefault();
    const orderId = document.getElementById('delivery-order-id').value;
    const code = document.getElementById('delivery-validation-code').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/deliveries/${orderId}/complete?validation_code=${code}`, { method: 'PUT' });
        if (response.ok) {
            closeDeliveryCodeModal();
            loadDeliveryDashboard();
        } else {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Invalid code'}`);
        }
    } catch (error) {
        console.error("Completion error", error);
    }
}


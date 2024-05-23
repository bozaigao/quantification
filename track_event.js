'use strict';

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (Math.random() * 16) | 0;
        var v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}
window.onload = () => {
    var Analytics = _analytics.init({
        app: 'analytics-html-demo',
        debug: true,
        plugins: []
    });

    Analytics.on('*', ({ payload }) => {
        console.log(`😁Steven Event ${payload.type}`, payload);
    });
    Analytics.track('ViewContent', {
        event_id: generateUUID(),
        event_name: 'ViewContent',
        event_time: new Date().getTime(),
        action_source: 'website',
        event_source_url: window.location.href,
        data_processing_options: ['LDU'],
        data_processing_options_country: 0,
        data_processing_options_state: 0,
        user_data: {
            em: [],
            ph: [],
            client_ip_address: '162.248.93.107',
            client_user_agent: navigator.userAgent,
            fbc: null,
            fbp: null,
            ge: null
        },
        custom_data: {
            content_type: 'product_group',
            content_ids: ['0400086839629'],
            currency: 'USD',
            value: 29.99,
            content_name: 'slim-fit cotton twill dress shirt'
        }
    });
    // Analytics.track('AddToCart', {
    //     event_id: generateUUID(),
    //     event_name: 'AddToCart',
    //     event_time: new Date().getTime(),
    //     action_source: 'website',
    //     event_source_url: window.location.href,
    //     data_processing_options: ['LDU'],
    //     data_processing_options_country: 0,
    //     data_processing_options_state: 0,
    //     user_data: {
    //         em: [],
    //         ph: [],
    //         client_ip_address: '162.248.93.107',
    //         client_user_agent: navigator.userAgent,
    //         fbc: null,
    //         fbp: null,
    //         ge: null
    //     },
    //     custom_data: {
    //         content_ids: ['0400086839629'],
    //         content_type: 'product_group',
    //         content_brands: ['Saks Fifth Avenue'],
    //         value: '29.99',
    //         currency: 'USD'
    //     }
    // });
    // Analytics.track('Purchase', {
    //     event_id: generateUUID(),
    //     event_name: 'Purchase',
    //     event_time: new Date().getTime(),
    //     action_source: 'website',
    //     event_source_url: window.location.href,
    //     data_processing_options: ['LDU'],
    //     data_processing_options_country: 0,
    //     data_processing_options_state: 0,
    //     user_data: {
    //         em: ['21132670d4e93c74333f6786fd4a08cbe24d49bb5d95bd0611761e846a5363b5'],
    //         ph: ['ed55218a1f760746572e3b7daeda47c94b3465163adbbfe9ece0a0e9e55be195'],
    //         client_ip_address: '162.248.93.107',
    //         client_user_agent: navigator.userAgent,
    //         fbc: null,
    //         fbp: null,
    //         ge: null,
    //         zp: '54bc216ded6b46ab2951c3d095e2ed8d5b5fa581ca8f84f4da758d2816662711'
    //     },
    //     custom_data: {
    //         contents: [
    //             {
    //                 id: '0400086839629',
    //                 quantity: 1
    //             }
    //         ],
    //         content_type: 'product_group',
    //         value: '29.99',
    //         currency: 'USD',
    //         delivery_category: 'home_delivery'
    //     }
    // });
};

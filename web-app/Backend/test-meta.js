import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

const metaAccessToken = process.env.META_ACCESS_TOKEN || '';
const phoneNumberId = process.env.META_PHONE_NUMBER_ID || '985139691354987';

async function test() {
    try {
        console.log("Sending to Meta...");
        const response = await axios.post(`https://graph.facebook.com/v17.0/${phoneNumberId}/messages`, {
            messaging_product: "whatsapp",
            recipient_type: "individual",
            to: "918807715828",
            type: "text",
            text: { preview_url: false, body: "Test free-form message" }
        }, {
            headers: {
                'Authorization': `Bearer ${metaAccessToken}`,
                'Content-Type': 'application/json'
            }
        });
        console.log("Success:", response.data);
    } catch (e) {
        console.log("Error details:");
        console.log(JSON.stringify(e.response?.data, null, 2));
    }
}
test();

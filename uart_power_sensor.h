#include "esphome.h"

class UartPowerSensor : public PollingComponent, public UARTDevice, public BinarySensor {
    public:
        UartPowerSensor(UARTComponent *parent, int id) : PollingComponent(5000), UARTDevice(parent), device_id(id) {}

        void setup() override { }

        int readline(int readch, uint8_t *buffer, int len) {
            static int pos = 0;
            int rpos;

            if (readch > 0) {
                switch (readch) {
                    case '\n': // Ignore new-lines
                    case 0x00: // Ignore Null
                    case 0x15: // Ignore NAK
                    case 0x06: // Ignore ACK
                        break;
                    case 0x0D: // Return on CR
                        rpos = pos;
                        pos = 0;  // Reset position index ready for next time
                        return rpos;
                    default:
                        if (pos < len-1) {
                            buffer[pos++] = readch;
                            buffer[pos] = 0;
                        }
                }
            }
            // No end of line has been found, so return -1.
            return -1;
        }

        float readvalue(uint8_t *buffer, int len) {
            int rpos = 0;
            memset(buffer, 0, len); // Clear buffer
            while (available()) {
                rpos = readline(read(), buffer, len);
                if (rpos > 0) break;
            }
            if (rpos < 3) return -1.0;

            // Validate response
            if (buffer[0] != 0x40) return -1.0; // '@'
            if (buffer[1] != device_id) return -1.0;
            if (buffer[2] != 0x41) return -1.0; // 'A'

            // Check power state
            if (buffer[3] == 0x30) { // '0'
                return 1.0; // ON
            } else if (buffer[3] == 0x31) { // '1'
                return 0.0; // OFF
            }

            return -1.0;
        }

        void update() override {
            // Clear Incoming and Outgoing serial data
            flush();
            while (available()) read();

            const int len = 5;

            // Request Status
            static uint8_t buffer[len] = {0x40, (uint8_t) device_id, 0x3F, 0x41, 0x0D}; // @1 ?A \n
            write_array(buffer, 5);
            flush();
            delay(100);

            // Read Response (if available)
            float value = readvalue(buffer, len);
            if (value != -1.0) publish_state(value == 1.0);
        }

    private:
        int device_id;

};

#include "esphome.h"

class UartPowerSensor : public PollingComponent, public UARTDevice, public BinarySensor {
    public:
        UartPowerSensor(UARTComponent *parent, int id) : PollingComponent(10000), UARTDevice(parent), device_id(id) {}

        void setup() override { }

        int readline(int readch, char *buffer, int len) {
            static int pos = 0;
            int rpos;

            if (readch > 0) {
                switch (readch) {
                    case '\n': // Ignore new-lines
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

        float readvalue(int readch, char *buffer, int len) {
            int rpos = 0;
            memset(buffer, 0, max_len); // Clear buffer
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
            const int max_len = 5;

            // Request Status
            static char buffer[max_len] = {0x40, device_id, 0x3F, 0x41, 0x0D}; // @1 ?A \n
            write(buffer, 5);
            delay(100);

            // Read Response (if available)
            float value = readvalue(buffer, max_len);
            if (value != -1.0) publish_state(value == 1.0);
        }

    private:
        int device_id;

};
